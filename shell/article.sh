#!/bin/bash
cur_dir=`dirname $0`
pythonfile="$cur_dir/../ArticleOutQueue.py"
today=`date +%Y%m%d`
logfile="$cur_dir/../logs/ArticleOutQueue$today.log"
interval=0
time1=`date "+%s"`
`/usr/bin/python3 $pythonfile  >>$logfile`