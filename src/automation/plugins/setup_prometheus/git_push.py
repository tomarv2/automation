import shutil
from automation.base.base_function import *
from automation.base.git_actions import *
import ruamel.yaml as yaml
import logging
from .config import (
    CONFIG_YAML_FILE
)

logger = logging.getLogger(__name__)


def update_github_prometheus(prometheus_rules_dir,
                             prometheus_static_files_dir,
                             prometheus_config_file,
                             project_name,
                             env):
    #
    # TODO: temp return true
    #
    #
    return True
    with open(CONFIG_YAML_FILE, 'r') as stream_config:
        out_config = yaml.load(stream_config)
        ssh_key_path = out_config['ssh_key_path'][0]
        branch = out_config['branch'][0]
        repo_path = out_config['prometheus']['monitoring']['repo']['path'][0]
        repo_url = out_config['prometheus']['monitoring']['repo']['url'][0]

    logger.debug("[prometheus] push to git")
    logger.debug("[prometheus] ssh_key_path: {}" .format(ssh_key_path))
    git_ssh_cmd = 'ssh -o StrictHostKeyChecking=no -i %s' % ssh_key_path
    prometheus_rules_path = os.path.join(repo_path, 'monitoring', 'rules', env)
    prometheus_static_files_path = os.path.join(repo_path, 'monitoring', 'static_files', env)
    prometheus_config_path = os.path.join(repo_path, 'monitoring','config')

    logger.debug("[prometheus] git_ssh_cmd: {}" .format(git_ssh_cmd))
    logger.debug("[prometheus] repo_path: {}" .format(repo_path))
    logger.debug("[prometheus] repo_url: {}" .format(repo_url))
    logger.debug("[prometheus] monitoring_env_directory: {}" .format(os.path.join(repo_path, 'monitoring')))
    logger.debug("[prometheus] prometheus_static_files_path: {}" .format(prometheus_static_files_path))
    logger.debug("[prometheus] prometheus_config_path: {}" .format(prometheus_config_path))

    try:
        logger.debug("[prometheus] verify if repo exists locally: {}" .format(repo_path))
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        repo_instance = clone_repo(git_ssh_cmd, repo_url, repo_path, branch)
    except BaseException:
        logger.error("[prometheus] unable to clone")
        raise SystemExit
    logger.debug("[prometheus] checkout branch: {}" .format(branch))
    checkout_branch(git_ssh_cmd, repo_instance, branch)

    # -------------------------------------------------------------------------
    #
    #    Update prometheus rules
    #
    # -------------------------------------------------------------------------
    logger.debug("[prometheus] list dir and copy from: {} to : {}" .format(prometheus_rules_dir, prometheus_rules_path))
    src_files = os.listdir(prometheus_rules_dir)
    for rule_file_name in src_files:
        rule_file_path = os.path.join(os.path.join(prometheus_rules_dir, rule_file_name))
        logger.debug("[prometheus] rules file path: {}" .format(rule_file_path))
        try:
            if os.path.isfile(rule_file_path):
                if not os.path.exists(prometheus_rules_path):
                    try:
                        os.makedirs(prometheus_rules_path)
                    except OSError:
                        logger.debug("directory does not exist")
                        pass
                try:
                    logger.debug("[prometheus] rules file name: {}" .format(os.path.join(prometheus_rules_path, rule_file_name)))
                    logger.debug("[prometheus] copying rule files: {}" .format(rule_file_path))
                    if not os.path.exists(os.path.join(prometheus_rules_path, rule_file_name)):
                        logger.debug("[prometheus] copying rules file")
                        try:
                            shutil.copy(rule_file_path, os.path.join(prometheus_rules_path, rule_file_name))
                        except:
                            logger.error("[prometheus] unable to copy rules file from: {} to {}" .format(rule_file_path, os.path.join(prometheus_rules_path, rule_file_name)))
                    else:
                        logger.debug("rule exist, then compare content")
                        if not compare_files(rule_file_path, os.path.join(prometheus_rules_path, rule_file_name)):
                            logger.debug("different content")
                            os.remove(os.path.join(prometheus_rules_path, rule_file_name))
                            shutil.copy(rule_file_path, os.path.join(prometheus_rules_path, rule_file_name))
                except BaseException:
                    logger.error("[prometheus] rules file copy failed")
        except BaseException:
            logger.error("[prometheus] directory/files already exists: {}" .format(prometheus_rules_path))

    # -------------------------------------------------------------------------
    #
    #    Update prometheus static files
    #
    # -------------------------------------------------------------------------
    logger.debug("[prometheus] list dir and copy from: {} to : {}" .format(prometheus_static_files_dir, prometheus_static_files_path))
    src_files = os.listdir(prometheus_static_files_dir)
    for static_file_name in src_files:
        logger.debug("[prometheus] copying static file: {}" .format(static_file_name))
        static_file_path = os.path.join(
            os.path.join(prometheus_static_files_dir, static_file_name))
        logger.debug("[prometheus] static_file_name: {}" .format(static_file_name))
        try:
            if os.path.isfile(static_file_path):
                if not os.path.exists(prometheus_static_files_path):
                    try:
                        os.makedirs(prometheus_static_files_path)
                    except OSError:
                        logger.error("directory does not exist")
                        pass
                try:
                    logger.debug("[prometheus] copying static files")
                    if not os.path.exists(os.path.join(prometheus_static_files_path, static_file_name)):
                        shutil.copy(static_file_path, os.path.join(prometheus_static_files_path, static_file_name))
                    else:
                        logger.debug("file exists")
                        if not compare_files(static_file_path, os.path.join(prometheus_static_files_path, static_file_name)):
                            logger.error("different content ")
                            os.remove(os.path.join(prometheus_static_files_path, static_file_name))
                            shutil.copy(static_file_path, os.path.join(prometheus_static_files_path, static_file_name))
                except BaseException:
                    logger.error("[prometheus] static_file copy failed")
        except BaseException:
            logger.error("[prometheus] directory/files already exists: {}" .format(prometheus_static_files_path))

    # -------------------------------------------------------------------------
    #
    #    Update prometheus config
    #
    # -------------------------------------------------------------------------
    for target in get_list_env(env):
        prometheus_config_path_env = os.path.join(prometheus_config_path, target)
        logger.debug("[prometheus] copy from: {} to : {}" .format(prometheus_config_file, os.path.join(prometheus_config_path,'config.yaml')))
        try:
            if os.path.isfile(prometheus_config_file):
                if not os.path.exists(prometheus_config_path_env):
                    try:
                        os.makedirs(prometheus_config_path_env)
                    except OSError:
                        logger.error("directory does not exist")
                        pass
                try:
                    logger.error("[prometheus] copying prometheus config file")
                    if not os.path.exists(os.path.join(prometheus_config_path_env, 'config.yaml')):
                        shutil.copy(
                            prometheus_config_file,
                            os.path.join(
                                prometheus_config_path_env,
                                'config.yaml'))
                    else:
                        logger.error("file exists")
                        if not compare_files(prometheus_config_file,os.path.join(prometheus_config_path_env, 'config.yaml')):
                            logger.error("different content")
                            os.remove(os.path.join(prometheus_config_path_env, 'config.yaml'))
                            shutil.copy(
                                prometheus_config_file,
                                os.path.join(
                                    prometheus_config_path_env, 'config.yaml'))
                except BaseException:
                    logger.error("[prometheus] config.yaml copy failed")
        except BaseException:
            logger.error(
                "[prometheus] directory/files already exists: {}" .format(
                    os.path.join(prometheus_config_path_env, 'config.yaml')))

    # -------------------------------------------------------------------------
    #
    #    Commit and push all changes
    #
    # -------------------------------------------------------------------------
    logger.error("[prometheus] git commit")
    commit_changes(git_ssh_cmd, repo_instance, branch, project_name)
    logger.error("[prometheus] git push")
    push_changes(git_ssh_cmd, repo_instance, branch)
