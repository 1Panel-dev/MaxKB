select model_id
from model_workspace_authorization
where case
          when authentication_type = 'WHITE_LIST' then
              %s = any (workspace_id_list)
          else
              not %s =  any(workspace_id_list)
          end