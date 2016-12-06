#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#<account>:<password>:<uid>:<gid>:<gecos>:<home directory>:<upload bandwidth>:
#<download bandwidth>:<upload ratio>:<download ratio>:<max number of connections>:
#<files quota>:<size quota>:<authorized local IPs>:<refused local IPs>:
#<authorized client IPs>:<refused client IPs>:<time restrictions>
#

DOCUMENTATION = '''
---
module: purepw
short_description: manage pureftpd virtual users.
'''

EXAMPLES = '''
- purepw:
    name: john
    password: W@rr|0r
    uid: 33
    gid: 33
    home_directory: /home/ftp/john
'''

RETURN = '''
status:
    description: update status
    returned: changed
    type: string
    sample: "updated"
'''

import bcrypt

from collections import OrderedDict
import os


def build_config_line(account, current_hashed_password, new_password):
    #keep current hashed password if same
    if current_hashed_password \
      and bcrypt.hashpw(new_password, current_hashed_password) == current_hashed_password:
        account['password'] = current_hashed_password
    else:
        #or make a new hash
        account['password'] = bcrypt.hashpw(new_password, bcrypt.gensalt())

    #config line with password
    return ':'.join(account.itervalues())


def mkdb(module):
    rc, stdout, stderr = module.run_command('pure-pw mkdb '+module.params['dbfile']+' -f '+module.params['passwdfile'],check_rc=True)
    return rc


def main():
    module = AnsibleModule(
        argument_spec = dict(
            state     = dict(default='present', choices=['present', 'absent']),
            name      = dict(required=True, type='str'),
            password  = dict(required=False, type='str', default=''),
            home_directory = dict(required=False, type='path', default=''),
            uid       = dict(required=False, type='str', default=''),
            gid       = dict(required=False, type='str', default=''),
            passwdfile = dict(required=False, default='/etc/pure-ftpd/pureftpd.passwd', type='str'),
            dbfile = dict(required=False, default='/etc/pure-ftpd/pureftpd.pdb', type='str')
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

    #module.fail_json(msg="Something fatal happened")

    #Check if database already exist
    if os.path.isfile(module.params['passwdfile']):

        #read current file
        f = open(module.params['passwdfile'], "r+")

        lines = f.readlines()

        for line in lines:
            #check if account is already present
            if line.startswith(module.params['name']+':'):

                account_config_line = build_config_line(account, line.split(':')[1], module.params['password'])

                #if same line than current, exit
                if line == account_config_line+"\n": #nothing to do
                    f.close
                    module.exit_json(changed=False)

                #if not, update
    		if module.check_mode:
        		module.exit_json(changed=True)

                f.seek(0)
                for l in lines:
                  if l.startswith(module.params['name']+':'):
                    f.write(account_config_line+"\n")
                  else:
                    f.write(l)
                f.truncate()
                f.close

                mkdb(module)

                module.exit_json(changed=True, status='updated')

        f.close


    ## account not already present or file is new

    if module.check_mode:
        module.exit_json(changed=True)

    account_config_line = build_config_line(account, None, module.params['password'])

    module.append_to_file(module.params['passwdfile'], account_config_line+"\n")

    mkdb(module)

    module.exit_json(changed=True, status='new')


from ansible.module_utils.basic import AnsibleModule
if __name__ == '__main__':
    main()
