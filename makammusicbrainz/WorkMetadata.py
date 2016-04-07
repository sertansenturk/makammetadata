from attribute import Attribute
import os
import json

import musicbrainzngs as mb
mb.set_useragent("Makam corpus metadata", "1.1", "compmusic.upf.edu")


class WorkMetadata(object):
    def __init__(self, print_warnings=None):
        self.print_warnings = print_warnings

    def from_musicbrainz(self, mbid):
        work = mb.get_work_by_id(mbid, includes=['artist-rels',
                                                 'recording-rels'])['work']

        data = ({'makam': [], 'form': [], 'usul': [], 'title': work['title'],
                 'mbid': mbid, 'composer': dict(), 'lyricist': dict()})

        # makam, form, usul attributes
        if 'attribute-list' in work.keys():
            w_attrb = work['attribute-list']

            makam = [a['attribute'] for a in w_attrb if 'Makam' in a['type']]
            data['makam'] = [
                {'mb_attribute': m,
                 'attribute_key': Attribute.get_attrib_key_from_mb_attrib(
                     m, 'makam'),
                 'source': 'http://musicbrainz.org/work/' + mbid}
                for m in makam]

            form = [a['attribute'] for a in w_attrb if 'Form' in a['type']]
            data['form'] = [
                {'mb_attribute': f,
                 'attribute_key': Attribute.get_attrib_key_from_mb_attrib(
                     f, 'form'),
                 'source': 'http://musicbrainz.org/work/' + mbid}
                for f in form]

            usul = [a['attribute'] for a in w_attrb if 'Usul' in a['type']]
            data['usul'] = [
                {'mb_attribute': u,
                 'attribute_key': Attribute.get_attrib_key_from_mb_attrib(
                     u, 'usul'),
                 'source': 'http://musicbrainz.org/work/' + mbid}
                for u in usul]

        # language
        if 'language' in work.keys():
            data['language'] = work['language']

        # composer and lyricist
        if 'artist-relation-list' in work.keys():
            for a in work['artist-relation-list']:
                if a['type'] == 'composer':
                    data['composer'] = {'name': a['artist']['name'],
                                        'mbid': a['artist']['id']}
                elif a['type'] == 'lyricist':
                    data['lyricist'] = {'name': a['artist']['name'],
                                        'mbid': a['artist']['id']}

        # add recordings
        data['recordings'] = []
        if 'recording-relation-list' in work.keys():
            for r in work['recording-relation-list']:
                data['recordings'].append({'mbid': r['recording']['id'],
                                           'title': r['recording']['title']})

        # add scores
        score_work_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'makam_data', 'symbTr_mbid.json')
        score_work = json.load(open(score_work_file, 'r'))
        data['scores'] = []
        for sw in score_work:
            if mbid in sw['uuid']:
                data['scores'].append(sw['name'])

        # warnings
        if self.print_warnings:
            if not data['makam']:
                print('http://musicbrainz.org/work/' + data['mbid'] +
                      ' Makam is not entered!')
            if not data['form']:
                print('http://musicbrainz.org/work/' + data['mbid'] +
                      ' Form is not entered!')
            if not data['usul']:
                print('http://musicbrainz.org/work/' + data['mbid'] +
                      ' Usul is not entered!')
            if not data['composer']:
                print('http://musicbrainz.org/work/' + data['mbid'] +
                      ' Composer is not entered!')
            if 'language' not in data.keys():
                if not data['lyricist']:
                    print('http://musicbrainz.org/work/' + data['mbid'] +
                          'Language is not entered!')
                else:
                    print('http://musicbrainz.org/work/' + data['mbid'] +
                          'Language of the vocal work is not entered!')
            else:
                if data['language'] == "zxx":  # no lyics
                    if data['lyricist']:
                        print('http://musicbrainz.org/work/' + data['mbid'] +
                              'Lyricist is entered to the instrumental work!')
                else:
                    if not data['lyricist']:
                        print('http://musicbrainz.org/work/' + data['mbid'] +
                              'Lyricist is not entered!')

        return data