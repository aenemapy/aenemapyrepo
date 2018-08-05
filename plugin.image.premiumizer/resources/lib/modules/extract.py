import zipfile,xbmcgui
dialog = xbmcgui.Dialog()

def all(_in, _out, dp=None):
    if dp:
        return allWithProgress(_in, _out, dp)

    return allNoProgress(_in, _out)
        

def allNoProgress(_in, _out):
    try:
        zin = zipfile.ZipFile(_in, 'r')
        zin.extractall(_out)
    except Exception, e:
        print str(e)
       

    return True


def allWithProgress(_in, _out, dp):

    zin = zipfile.ZipFile(_in,  'r')

    nFiles = float(len(zin.infolist()))
    count  = 0
    errors = 0
    try:
        for item in zin.infolist():
            count += 1
            update = count / nFiles * 100
            filenamefull = item.filename


            dp.update(int(update),'Extracting... Errors:  ' + str(errors) ,filenamefull, '')
            try: zin.extract(item, _out)
            except Exception, e:
				errors += 1
				choice = xbmcgui.Dialog().yesno('Error!', filenamefull , str(e), nolabel='Exit',yeslabel='Continue')
				if choice == 0:break
				elif choice == 1:pass
					
				
    except Exception, e:
        print str(e)
        

    return True