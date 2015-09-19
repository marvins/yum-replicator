__author__ = 'ms6401'


#  Python Libraries


class Yum_Repo(object):

    def __init__(self):
        pass


class Repo_Manager(object):

    #  Repositories
    repos = []

    def __init__(self,options):

        #  Get list of repositories
        self.repos = self.Load_Repositories()


    def Load_Repositories(self):

        #  Get list of repos on the system
        pass