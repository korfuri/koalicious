#!/usr/bin/python2.4

import grp
import os
import pwd
import sys

def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    uid = os.getuid()
    gid = os.getgid()
    target_uid = pwd.getpwnam(uid_name)[2]
    target_gid = grp.getgrnam(gid_name)[2]

    if uid == target_uid and gid == target_gid:
        return True
    if uid != 0:
        return False
    try:
        os.setgid(target_gid)
        os.setuid(target_uid)
    except OSError, e:
        return False

    final_uid = os.getuid()
    final_gid = os.getgid()
    if final_uid != target_uid or final_gid != target_gid:
        print 'Panic: setuid or setgid silently failed.'
        sys.exit(-1)

    return True
