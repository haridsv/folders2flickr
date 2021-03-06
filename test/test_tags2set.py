"""
Test case for tags2set.py
"""
import logging
import sys
import os
import unittest
import tempfile
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import fakeflickr
import shelve

def addinvert(dictthing):
    """
    Add the keys and values, but inverted to the dictionary
    """
    keys = dictthing.keys()
    for key in keys:
        newkey = dictthing[key]
        dictthing[newkey] = key

class Tags2SetTest(unittest.TestCase):
    """
    Test suite for tags2set.py
    """
    def setUp(self):
        user = fakeflickr.fakelogin()
        user.clearPhotosetsInternal()
        inifile = open('uploadr.ini', 'w')
        sample = open('uploadr.ini.sample', 'r')
        inifile.write(sample.read())
        inifile.close()
        import f2flickr.tags2set

    def tearDown(self):
        os.unlink('uploadr.ini')

    def testSetIsUpdated(self):
        """
        Check that when updating in batches, the set is updated.
        First upload 20 photos, then upload some more, up to 44
        The 44 should be in the set.
        """
        import f2flickr.tags2set
        historyFile = tempfile.mktemp()
        fakeuploaded = shelve.open(historyFile)
        for i in range(1, 21):
            fakeuploaded[str(i)] = 'random/img%d.jpg' % i

        addinvert(fakeuploaded)
        fakeuploaded.close()

        uploaded = [str(r) for r in range(1, 21)]
        f2flickr.tags2set.createSets(uploaded, historyFile)
        user = fakeflickr.fakelogin()
        self.assertEquals(1, len(user.getPhotosets()))

        fakeuploaded = shelve.open(historyFile)
        for i in range(1, 45):
            fakeuploaded[str(i)] = 'random/img%d.jpg' % i
        addinvert(fakeuploaded)
        fakeuploaded.close()

        uploaded = [str(r) for r in range(22, 45)]
        f2flickr.tags2set.createSets(uploaded, historyFile)
        user = fakeflickr.fakelogin()
        self.assertEquals(1, len(user.getPhotosets()))

        ps = user.getPhotosets()[0]
        photos = ps.getPhotos()
        self.assertEquals(44, len(photos))

        os.remove(historyFile)

    def createHistory(self):
        historyFile = tempfile.mktemp()
        fakeuploaded = shelve.open(historyFile)
        for i in range(1, 3):
            fakeuploaded[str(i)] = 'holidays/Crete/img%d.jpg' % i
        uploaded = []
        uploaded[:] = fakeuploaded.keys()
        addinvert(fakeuploaded)
        fakeuploaded.close()
        return uploaded, historyFile

    def testOnlySubsFalse(self):
        """
        Check only_sub_sets = false
        """
        import f2flickr.tags2set
        uploaded, historyFile = self.createHistory()
        f2flickr.configuration.configdict = f2flickr.configuration.ConfigDict()
        f2flickr.tags2set.createSets(uploaded, historyFile)
        user = fakeflickr.fakelogin()
        self.assertEquals(1, len(user.getPhotosets()))
        ps = user.getPhotosets()[0]
        self.assertEquals('holidays Crete', ps.title)


    def testOnlySubsTrue(self):
        """
        Check only_sub_sets = false
        """
        import f2flickr.tags2set
        import f2flickr.configuration
        uploaded, historyFile = self.createHistory()
        tmp = open('uploadr.ini', 'r')
        lines = tmp.readlines()
        tmp.close()
        tmp = open('uploadr.ini', 'w')
        for line in lines:
            if line.startswith('only_sub_sets'):
                line = line.replace('false', 'true')
            tmp.write(line)
        tmp.close()
        f2flickr.configuration.configdict = f2flickr.configuration.ConfigDict()
        f2flickr.tags2set.createSets(uploaded, historyFile)
        user = fakeflickr.fakelogin()
        self.assertEquals(1, len(user.getPhotosets()))
        ps = user.getPhotosets()[0]
        self.assertEquals('Crete', ps.title)


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(levelname)s %(message)s',
                filename='debug.log',
                filemode='w')
    logging.debug('Started')
    unittest.main()
