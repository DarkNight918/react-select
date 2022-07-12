#!/usr/bin/env python
import argparse
import errno
import os
import stat
import shutil
from datetime import datetime
from datetime import timedelta
from random import randint
from subprocess import Popen
import sys

# NUM = 366


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def main(def_args=sys.argv[1:]):
    args = arguments(def_args)
    curr_date = datetime.now()
    directory = 'repository-' + curr_date.strftime('%Y-%m-%d-%H-%M-%S')
    repository = args.repository
    user_name = args.user_name
    user_email = args.user_email
    if repository is not None:
        start = repository.rfind('/') + 1
        end = repository.rfind('.')
        directory = repository[start:end]
    no_weekends = args.no_weekends
    frequency = args.frequency
    # if os.path.exists(directory):
    #     shutil.rmtree(directory, onerror=remove_readonly)
    # os.mkdir(directory)
    # os.chdir(directory)
    # run(['git', 'init'])

    if user_name is not None:
        run(['git', 'config', 'user.name', user_name])

    if user_email is not None:
        run(['git', 'config', 'user.email', user_email])

    if args.start_date is None:
        NUM = args.days_ago
        start_date = curr_date.replace(hour=20, minute=0) - timedelta(NUM)
    else:
        start_date = datetime.strptime(args.start_date, "%Y/%m/%d, %H:%M:%S")
        NUM = (curr_date.replace(hour=20, minute=0) - start_date).days
    for day in (start_date + timedelta(n) for n in range(NUM)):
        if (not no_weekends or day.weekday() < 5) \
                and randint(0, 100) < frequency:
            for commit_time in (day + timedelta(minutes=m)
                                for m in range(contributions_per_day(args))):
                contribute(commit_time)

    if repository is not None:
        run(['git', 'remote', 'add', 'origin', repository])
        run(['git', 'branch', '-M', 'main'])
        run(['git', 'push', '-u', 'origin', 'main'])

    print('\nRepository generation ' +
          '\x1b[6;30;42mcompleted successfully\x1b[0m!')


def contribute(date):
    with open(os.path.join(os.getcwd(), 'history.md'), 'a') as file:
        file.write(message(date) + '\n\n')
    run(['git', 'add', '.'])
    run(['git', 'commit', '-m', '"%s"' % message(date),
         '--date', date.strftime('"%Y-%m-%d %H:%M:%S"')])


def run(commands):
    Popen(commands).wait()


def message(date):
    return date.strftime('Contribution: %Y-%m-%d %H:%M')


def contributions_per_day(args):
    max_c = args.max_commits
    if max_c > 20:
        max_c = 20
    if max_c < 1:
        max_c = 1
    return randint(1, max_c)


def arguments(argsval):
    parser = argparse.ArgumentParser()
    parser.add_argument('-nw', '--no_weekends',
                        required=False, action='store_true', default=False,
                        help="""do not commit on weekends""")
    parser.add_argument('-mc', '--max_commits', type=int, default=7,
                        required=False, help="""Defines the maximum amount of
                        commits a day the script can make. Accepts a number
                        from 1 to 20. If N is specified the script commits
                        from 1 to N times a day. The exact number of commits
                        is defined randomly for each day. The default value
                        is 10.""")
    parser.add_argument('-fr', '--frequency', type=int, default=80,
                        required=False, help="""Percentage of days when the
                        script performs commits. If N is specified, the script
                        will commit N%% of days in a year. The default value
                        is 80.""")
    parser.add_argument('-r', '--repository', type=str, required=False,
                        help="""A link on an empty non-initialized remote git
                        repository. If specified, the script pushes the changes
                        to the repository. The link is accepted in SSH or HTTPS
                        format. For example: git@github.com:user/repo.git or
                        https://github.com/user/repo.git""")
    parser.add_argument('-un', '--user_name', type=str, required=False, default="DevGroupInc",
                        help="""Overrides user.name git config.
                        If not specified, the global config is used.""")
    parser.add_argument('-ue', '--user_email', type=str, required=False, default="BlueDragon0123@outlook.com",
                        help="""Overrides user.email git config.
                        If not specified, the global config is used.""")
    parser.add_argument('-da', '--days_ago', type=int, required=False, default=25,
                        help="""Show them if you want to contribute a few days in advance.""")
    parser.add_argument('-sd', '--start_date', type=str, required=False,
                        help="""Start Date.""")
    return parser.parse_args(argsval)


if __name__ == "__main__":
    main()
