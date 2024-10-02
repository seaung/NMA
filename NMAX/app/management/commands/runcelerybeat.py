import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '运行celery beat定时调度后台'

    def add_arguments(self, parser):
        parser.add_argument('--loglevel', default='DEBUG', type=str, help='指定日志输出等级')

    def handle(self, *args, **options):
        cmds = ['celery', '-A', 'app.configs.celery', 'beat']

        if options.get('loglevel'):
            cmds.extend(['--loglevel', options.get('loglevel')])

        try:
            self.stdout.write('[+] starting celery beat...')
            subprocess.run(cmds, check=True)
        except subprocess.CalledProcessError as e:
            self.stderr.write(f'[-] run celery beat error : {e}')
        except KeyboardInterrupt:
            self.stdout.write('[!] shutdown celery beat deamon...')
