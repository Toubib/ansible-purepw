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
#TEST: ansible@puppet:~/git/ansible-purepw$ ../ansible/hacking/test-module -m ./purepw.py -a 'password=test2 name=test2 passwdfile=/tmp/test1.pwd uid=33 gid=33 home_directory=/home/ftp/test1 salt="$2a$12$meXQDD3hW/uEiwmN0SoHu"'


import bcrypt

from collections import OrderedDict
import os

def main():
    module = AnsibleModule(
        argument_spec = dict(
            state     = dict(default='present', choices=['present', 'absent']),
            name      = dict(required=True, type='str'),
            password  = dict(required=False, type='str', default=''),
            salt      = dict(required=False, type='str', default=bcrypt.gensalt()),
            home_directory = dict(required=False, type='path', default=''),
            uid       = dict(required=False, type='str', default=''),
            gid       = dict(required=False, type='str', default=''),
            passwdfile = dict(required=False, default='/etc/pure-ftpd/pureftpd.passwd', type='str')
        ),
        supports_check_mode=True
    )

    account = OrderedDict((
        ('account', module.params['name']),
        ('password', None),
        ('uid', module.params['uid']),
        ('gid', module.params['gid']),
        ('gecos', ''),
        ('home_directory', module.params['home_directory']+'./'),
        ('upload_bandwidth', ''),
        ('download_bandwidth', ''),
        ('upload_ratio', ''),
        ('download_ratio', ''),
        ('max_number_of_connections', ''),
        ('files_quota', ''),
        ('size_quota', ''),
        ('authorized_local_ips', ''),
        ('refused_local_ips', ''),
        ('authorized_client_ips', ''),
        ('refused_client_ips', ''),
        ('time_restrictions', '')
    ))

    if module.check_mode:
        module.exit_json(changed=check_if_system_state_would_be_changed())

    hashed_password = bcrypt.hashpw(module.params['password'], module.params['salt'])

    #module.fail_json(msg="Something fatal happened")
    account['password'] = hashed_password

    account_config_line = ':'.join(account.itervalues())

    #Check if database already exist
    if os.path.isfile(module.params['passwdfile']):

        #read current file
        f = open(module.params['passwdfile'], "r+")

        lines = f.readlines()

        for line in lines:
            #check if account is already well configured
            if line == account_config_line+"\n": #nothing to do
                f.close
                module.exit_json(changed=False)

            #check if account is already present with other parameters
            elif line.startswith(module.params['name']+':'):
                f.seek(0)
                for l in lines:
                  if l.startswith(module.params['name']+':'):
                    f.write(account_config_line+"\n")
                  else:
                    f.write(l)
                f.truncate()
                f.close

                rc, stdout, stderr = module.run_command('pure-pw mkdb /tmp/test.db -f '+module.params['passwdfile'],check_rc=True)
                module.exit_json(changed=True, status='updated')

        f.close


    #account not already present or file is new
    module.append_to_file(module.params['passwdfile'], account_config_line+"\n")

    rc, stdout, stderr = module.run_command('pure-pw mkdb /tmp/test.db -f '+module.params['passwdfile'],check_rc=True)

    module.exit_json(changed=True, status='newline')


def check_if_system_state_would_be_changed():
    changed = False
    return changed

from ansible.module_utils.basic import AnsibleModule
if __name__ == '__main__':
    main()
