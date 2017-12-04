DEST=${VIRTUAL_ENV}/lib/python2.7/site-packages/ansible/

rm -rf $DEST/modules/hashivault
rm -f $DEST/module_utils/hashivault.py
rm -f $DEST/plugins/lookup/hashivault.py

ln -s $PWD/ansible/modules/hashivault $DEST/modules/hashivault
ln $PWD/ansible/module_utils/hashivault.py $DEST/module_utils/hashivault.py
ln $PWD/ansible/plugins/lookup/hashivault.py $DEST/plugins/lookup/hashivault.py

