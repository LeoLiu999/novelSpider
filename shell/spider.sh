#!/bin/bash
cur_dir=`dirname $0`
pythonfile="$cur_dir/../Crawl.py"
today=`date +%Y%m%d`
logfile="$cur_dir/../logs/Crawl$today.log"
interval=0
time1=`date "+%s"`
`/usr/bin/python3 $pythonfile  >>$logfile`