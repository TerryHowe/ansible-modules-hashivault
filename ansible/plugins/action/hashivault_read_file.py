from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash

class ActionModule(ActionBase):

    # copied from `ansible.plugins.action.template`
    def _get_copy_action_plugin(self):
        return (self._shared_loader_obj.action_loader.get(
            'copy',
            task=self._task.copy(),
            connection=self._connection,
            play_context=self._play_context,
            loader=self._loader,
            templar=self._templar,
            shared_loader_obj=self._shared_loader_obj))


    def run(self, tmp=None, task_vars=None):

        if task_vars is None:
            task_vars = dict()

        results = super(ActionModule, self).run(tmp, task_vars)

        args = self._task.args.copy()

        dest = args.pop('dest')
        mode = args.pop('mode',None)
        force = args.pop('force',False)

        results = merge_hash(
            results,
            self._execute_module(module_name='hashivault_read', tmp=tmp, task_vars=task_vars, module_args=args)
        )

        if 'failed' in results and results['failed'] == True:
            return results

        content = results.pop('value')

        if content == None:
            results['failed'] = True
            results['msg'] = 'Could not find file `%s` in secret `%s`'%(args['key'],args['secret'])
            return(results)


        new_module_args = {
            'dest':dest,
            'content':content.decode('base64'),
            'force':force,
            'mode':mode
        }
        self._update_module_args('copy',new_module_args,task_vars)

        # `copy` module uses an action plugin, so we have to execute
        # the plugin instead of directly executing the module
        copy_action = self._get_copy_action_plugin()
        copy_action._task.args = new_module_args
        results = merge_hash(
            results,
            copy_action.run(task_vars=task_vars)
        )

        if force == False and results['changed'] == False:
            results['failed'] = True
            results['msg'] = 'File %s already exists. Use `force: true` to overwrite'%dest

        return(results)