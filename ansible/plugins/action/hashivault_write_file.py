from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash

class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):

        if task_vars is None:
            task_vars = dict()

        results = super(ActionModule, self).run(tmp, task_vars)

        args = self._task.args.copy()

        key = args.pop('key')
        path = args.pop('path')

        new_module_args = {
            'src':path
        }
        self._update_module_args('slurp',new_module_args,task_vars)

        results = merge_hash(
            results,
            self._execute_module(module_name='slurp', tmp=tmp, task_vars=task_vars, module_args=new_module_args)
        )

        if 'failed' in results and results['failed'] == True:
            return(results)

        #already base64 encoded from slurp
        content = results.pop('content')


        args['data'] = { key:content }

        results = merge_hash(
            results,
            self._execute_module(module_name='hashivault_write', tmp=tmp, task_vars=task_vars, module_args=args)
        )

        results['invocation']['module_args']['data'] = 'VALUE_SPECIFIED_IN_NO_LOG_PARAMETER'

        return(results)