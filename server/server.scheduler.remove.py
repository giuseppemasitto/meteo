from crontab import CronTab
 
remover = CronTab(user='pi')
for job in remover:
    if job.comment == 'uploader':
        remover.remove(job)
        remover.write()
