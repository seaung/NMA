import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '运行celery后台工作队列'

    def add_arguments(self, parser):
        parser.add_argument('--loglevel', default='DEBUG', type=str, help='指定celery日志输出等级')
        parser.add_argument('--concurrency', default=3, type=int, help='指定celery work并发数量')

    def handle(self, *args, **options):
        cmds = ['celery', '-A', 'app.configs.celery', 'worker']

        if options.get('loglevel'):
            cmds.extend(['--loglevel', options.get('loglevel')])

        if options.get('concurrent'):
            cmds.extend(['--concurrent', str(options.get('concurrent'))])

        try:
            self.stdout.write('[+] starting celery worker...')
            subprocess.run(cmds, check=True)
        except subprocess.CalledProcessError as e:
            self.stderr.write(f'[-] run celery worker error : {e}')
        except KeyboardInterrupt:
            self.stdout.write('[!] shutdown celery worker deamon...')
