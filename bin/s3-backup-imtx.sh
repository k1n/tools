#!/bin/sh
# UTCOM Backup scripts
# To easily backup UTCOM Project
# Author: TualatriX

set -e
set -x
 
REMOTE_PATH="$HOME/public_html/imtx.me"
PROJECT_NAME="imtx"
LOCAL_PATH="$HOME/Dropbox/$PROJECT_NAME-backup"
PRE=$PROJECT_NAME-`date +%F`
KERNEL=`uname -s`
 
if [ ! -e $LOCAL_PATH/$PROJECT_NAME ]
then
	mkdir -p $LOCAL_PATH/$PROJECT_NAME
fi


cd $REMOTE_PATH; tar cf - --exclude '.git' $PROJECT_NAME | gzip > $LOCAL_PATH/$PRE.tar.gz

cd $LOCAL_PATH

tar zxvf $PRE.tar.gz $PROJECT_NAME/$PROJECT_NAME/local_settings.py
touch $PROJECT_NAME/$PROJECT_NAME/__init__.py

cd $LOCAL_PATH/$PROJECT_NAME

if [ -f $PROJECT_NAME/local_settings.py ];then
    if [ $KERNEL = "Darwin" ]; then
        gsed -i '/global_setting/d' $PROJECT_NAME/local_settings.py
    elif [ $KERNEL = "Linux" ]; then
        sed -i '/global_setting/d' $PROJECT_NAME/local_settings.py
    fi

    DB_NAME=`python -c "import $PROJECT_NAME.local_settings;print $PROJECT_NAME.local_settings.DATABASES['default']['NAME']"`
    DB_USER=`python -c "import $PROJECT_NAME.local_settings;print $PROJECT_NAME.local_settings.DATABASES['default']['USER']"`
    DB_PASSWORD=`python -c "import $PROJECT_NAME.local_settings;print $PROJECT_NAME.local_settings.DATABASES['default']['PASSWORD']"`
    rm -r $PROJECT_NAME
else
    echo "Something wrong ..."
    exit 1
fi

cd $LOCAL_PATH

mysqldump -u${DB_USER} -p${DB_PASSWORD} $DB_NAME | gzip > $PRE.sql.gz

s3cmd put $LOCAL_PATH/$PRE.tar.gz s3://imtx/
s3cmd put $LOCAL_PATH/$PRE.sql.gz s3://imtx/
