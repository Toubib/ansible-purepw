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

from collections import OrderedDict

def main():
    module = AnsibleModule(
        argument_spec = dict(
            state     = dict(default='present', choices=['present', 'absent']),
            name      = dict(required=True, type='str'),
            password  = dict(required=False, type='str', default=''),
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

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(module.params['password'], salt)

    #module.fail_json(msg="Something fatal happened")
    account['password'] = hashed_password

    module.append_to_file(module.params['passwdfile'], ':'.join(account.itervalues()) + "\n")

    rc, stdout, stderr = module.run_command('pure-pw mkdb /tmp/test.db -f '+module.params['passwdfile'],check_rc=True)

    module.exit_json(changed=True, hashed_password=hashed_password)

def check_if_system_state_would_be_changed():
    changed = False
    return changed

from ansible.module_utils.basic import AnsibleModule
if __name__ == '__main__':
    main()
