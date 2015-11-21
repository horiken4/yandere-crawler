# coding: utf-8

import argparse
import urllib2
import xml.etree.ElementTree as ET
import time
import json
import os.path


def main():
    parser = argparse.ArgumentParser(description='yande.re crawler')
    parser.add_argument('--begin_page', metavar='begin_page', type=int, default=1, help='Max page')
    parser.add_argument('--end_page', metavar='end_page', type=int, default=1, help='Max page')
    parser.add_argument('output_dir', metavar='output_dir', type=str, help='Output directory')
    args = parser.parse_args()

    # Check total page

    max_page = 0

    try:
        res = urllib2.urlopen('https://yande.re/post.xml')
        root = ET.fromstring(res.read())
        max_page = int(root.attrib['count']) / 100 + 1
    except urllib2.URLError, e:
        print 'Failed to download (reason = {0})'.format(e.reason)
    except urllib2.HTTPError, e:
        print 'Failed to download (respose code = {0})'.format(e.code)
    finally:
        if res is not None:
            res.close()

    if args.end_page < max_page:
        max_page = args.end_page

    min_page = args.begin_page
    if min_page < 1:
        min_page = 1

    # Download meta data and image

    file_list = []
    for page in range(min_page, max_page + 1):
        try:
            url = 'http://yande.re/post.json?page={0}&limit=5'.format(page)
            print url
            res = urllib2.urlopen(url)
            metas = json.JSONDecoder().decode(res.read())

            for meta in metas:

                # Make output directory
                illust_id = long(meta['id'])
                mdir = str(illust_id / 1000)
                preview_odir = os.path.join(args.output_dir, 'preview', mdir)
                if not os.path.isdir(preview_odir):
                    os.makedirs(preview_odir)
                meta_odir = os.path.join(args.output_dir, 'meta', mdir)
                if not os.path.isdir(meta_odir):
                    os.makedirs(meta_odir)

                # Save meta data
                meta_fpath = '{0}/{1}.json'.format(meta_odir, illust_id)
                with open(meta_fpath, 'w') as f:
                    json.dump(meta, f)

                # Save preview image
                preview_url = meta['preview_url']
                print preview_url
                preview_res = urllib2.urlopen(preview_url)
                preview_fpath = '{0}/{1}.jpg'.format(preview_odir, illust_id)
                with open(preview_fpath, 'wb') as f:
                    f.write(preview_res.read())

                file_list.append([str(illust_id), os.path.relpath(meta_fpath, args.output_dir), os.path.relpath(preview_fpath, args.output_dir)])

                time.sleep(1.0)

            time.sleep(1.0)
        except urllib2.URLError, e:
            print 'Failed to download (reason = {0})'.format(e.reason)
        except urllib2.HTTPError, e:
            print 'Failed to download (respose code = {0})'.format(e.code)
        finally:
            if res is not None:
                res.close()

    with open(os.path.join(args.output_dir, 'list.txt'), 'w') as f:
        for line in file_list:
            f.write(' '.join(line) + '\n')

if __name__ == '__main__':
    main()
