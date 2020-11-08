########################################################################
#
# Developed for AT&T by Nicholas Gibson, August 2017
#
# Action plugin for hashivault_read_to_file module.
#
# Reads file/secret from Vault  on localhost using hashivault_read module.
# Decodes from base64 and stores file on remote host using copy module.
#
########################################################################

import base64 as base64encode
import os
import tempfile

from ansible.playbook.play_context import PlayContext
from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash


class ActionModule(ActionBase):

    # load and return ansible copy action plugin
    # copied from `ansible/plugins/action/template.py`
    def _get_copy_action_plugin(self, connection):
        return (self._shared_loader_obj.action_loader.get(
            'copy',
            task=self._task.copy(),
            connection=connection,
            play_context=self._play_context,
            loader=self._loader,
            templar=self._templar,
            shared_loader_obj=self._shared_loader_obj))

    def run(self, tmp=None, task_vars=None):

        if task_vars is None:
            task_vars = dict()

        results = super(ActionModule, self).run(tmp, task_vars)

        args = self._task.args.copy()

        dest = args.pop('dest', None)
        force = args.pop('force', True)
        base64 = args.pop('base64', True)

        new_module_args = {
            'dest': dest,
            'force': force,
        }
        copy_attributes = [
            'attributes',
            'backup',
            'checksum',
            'delimiter',
            'directory_mode',
            'follow',
            'group',
            'local_follow',
            'mode',
            'owner',
            'regexp',
            'selevel',
            'serole',
            'setype',
            'seuser',
            'unsafe_writes',
            'validate',
        ]
        for attribute in copy_attributes:
            value = args.pop(attribute, None)
            if value is not None:
                new_module_args[attribute] = value

        become = self._play_context.become
        become_method = self._play_context.become_method

        old_connection = self._connection
        self._connection = self._shared_loader_obj.connection_loader.get('local', PlayContext(),
                                                                         old_connection._new_stdin)
        self._play_context.become = False
        self._play_context.become_method = None

        results = merge_hash(
            results,
            # executes hashivault_read module on localhost
            self._execute_module(module_name='hashivault_read', tmp=tmp, task_vars=task_vars, module_args=args)
        )

        if 'failed' in results and results['failed'] is True:
            return results

        content = results.pop('value', None)

        if content is None:
            results['failed'] = True
            results['rc'] = 1
            results['msg'] = u'Could not find file `%s` in secret `%s`' % (args['key'], args['secret'])
            return results

        # write to temp file on ansible host to copy to remote host
        local_tmp = tempfile.NamedTemporaryFile(delete=False)
        if base64:
            try:
                content = base64encode.b64decode(content)
            except Exception as ex:
                results['failed'] = True
                results['rc'] = 1
                secret_key = str(args.pop('secret', 'secret')) + "/" + str(args.pop('key', ''))
                results['msg'] = u'Error base64 decoding secret %s: %s' % (secret_key, str(ex))
                return results
        else:
            try:
                import sys
                if sys.version_info[0] > 2:
                    content = bytes(content, 'utf-8')
                else:
                    content = bytes(content)
            except Exception as ex:
                results['failed'] = True
                results['rc'] = 1
                secret_key = str(args.pop('secret', 'secret')) + "/" + str(args.pop('key', ''))
                results['msg'] = u'Error preparing utf-8 secret %s: %s' % (secret_key, str(ex))
                return results
        local_tmp.write(content)
        local_tmp.close()
        new_module_args['src'] = local_tmp.name

        self._update_module_args('copy', new_module_args, task_vars)

        # `copy` module uses an action plugin, so we have to execute
        # the plugin instead of directly executing the module
        copy_action = self._get_copy_action_plugin(old_connection)
        copy_action._task.args = new_module_args
        copy_action._play_context.become = become
        copy_action._play_context.become_method = become_method

        results = merge_hash(
            results,
            # executes copy action plugin/module on remote host
            copy_action.run(task_vars=task_vars)
        )

        # remove temp file
        os.unlink(local_tmp.name)

        if force is False and results['changed'] is False:
            results['failed'] = True
            results['rc'] = 1
            results['msg'] = u'File %s already exists. Use `force: true` to overwrite' % dest

        return results
