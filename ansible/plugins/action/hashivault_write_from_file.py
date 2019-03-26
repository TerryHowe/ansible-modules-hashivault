########################################################################
#
# Developed for AT&T by Nicholas Gibson, August 2017
#
# Action plugin for hashivault_write_from_file module.
#
# Reads file from remote host using slurp module. (base64 encoded)
# Stores file/secret to Vault using hashivault_read module on localhost.
#
########################################################################

from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):

        if task_vars is None:
            task_vars = dict()

        results = super(ActionModule, self).run(tmp, task_vars)

        args = self._task.args.copy()

        key = args.pop('key', None)
        path = args.pop('path', None)

        new_module_args = {
            'src': path
        }
        self._update_module_args('slurp', new_module_args, task_vars)

        results = merge_hash(
            results,
            # executes slurp module on remote host
            self._execute_module(module_name='slurp', tmp=tmp, task_vars=task_vars, module_args=new_module_args)
        )

        if 'failed' in results and results['failed'] is True:
            return results

        # already base64 encoded from slurp
        content = results.pop('content', None)

        self._play_context.become = False
        self._play_context.become_method = None

        self._connection = self._shared_loader_obj.connection_loader.get('local', self._play_context,
                                                                         self._connection._new_stdin)

        args['data'] = {key: content}
        if 'update' not in args:
            args['update'] = True

        results = merge_hash(
            results,
            # executes hashivault_write module on localhost
            self._execute_module(module_name='hashivault_write', tmp=tmp, task_vars=task_vars, module_args=args)
        )

        results['invocation']['module_args']['data'] = 'VALUE_SPECIFIED_IN_NO_LOG_PARAMETER'

        return results
