#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Files storing virtual users have one line per user. These lines have the following syntax:
#
#<account>:<password>:<uid>:<gid>:<gecos>:<home directory>:<upload bandwidth>:
#<download bandwidth>:<upload ratio>:<download ratio>:<max number of connections>:
#<files quota>:<size quota>:<authorized local IPs>:<refused local IPs>:
#<authorized client IPs>:<refused client IPs>:<time restrictions>
#
#user:pass:uid:gid::path/./::::::::::::
#
#TEST: ./ansible/hacking/test-module -m ./purepw.py -a "password=test name=test1 passwdfile=/tmp/test1.pwd uid=33 gid=33 path=/home/ftp/test1"

import bcrypt

def main():
    module = AnsibleModule(
        argument_spec = dict(
            state     = dict(default='present', choices=['present', 'absent']),
            name      = dict(required=True, type='str'),
            password  = dict(required=False, type='str'),
            path      = dict(required=False, type='path'),
            uid       = dict(required=False, type='str'),
            gid       = dict(required=False, type='str'),
            passwdfile = dict(required=False, default='/etc/pure-ftpd/pureftpd.passwd', type='str')
        ),
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(changed=check_if_system_state_would_be_changed())

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(module.params['password'], salt)

    #module.fail_json(msg="Something fatal happened")

    line=module.params['name']+':'+hashed_password+':'+module.params['uid']+':'+module.params['gid']+':'+':'+module.params['path']+'./'+'::::::::::::'+"\n"

    module.append_to_file(module.params['passwdfile'], line)

    rc, stdout, stderr = module.run_command('pure-pw mkdb /tmp/test.db -f '+module.params['passwdfile'],check_rc=True)

    module.exit_json(changed=True, hashed_password=hashed_password)

def check_if_system_state_would_be_changed():
    changed = False
    return changed

from ansible.module_utils.basic import AnsibleModule
if __name__ == '__main__':
    main()
