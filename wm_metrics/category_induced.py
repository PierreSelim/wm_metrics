# -*- coding: utf-8 -*-
#!/usr/bin/python

import mw_api, mw_util, json, codecs, MySQLdb, operator

class CategoryInduced:
    def __init__(self, category):
        self.commons = mw_api.MwWiki(url_api='https://commons.wikimedia.org/w/api.php')
        self.category = category.replace(" ", "_").decode('utf-8')
        self.categories = []
        self.first_images = []
        """"DB instantiation"""
        self.db = MySQLdb.connect(host="commonswiki.labsdb", db="commonswiki_p", read_default_file="~/replica.my.cnf", charset='utf8')
        self.cursor = self.db.cursor()
        #TODO: prendre que des images
        self.query = """SELECT page.page_title
                        FROM page
                        JOIN categorylinks ON page.page_id = categorylinks.cl_from
                        WHERE categorylinks.cl_to = %s
                        ORDER BY categorylinks.cl_timestamp ASC
                        LIMIT 1;"""

 
    def list_category(self):
        import os.path
        cache_name = "cache/%s.cache" % (self.category)
        result = None
        if os.path.exists(cache_name):
            cache = codecs.open(cache_name, 'r', 'utf-8')
            result = json.loads(cache.read())
        else:
            result = json.loads(self.commons.send_to_api(mw_api.MwApiQuery(
                properties={
                    "prop"	: "categories",
                    "cllimit" : "max",
                    "clir" : "ascending",
                    "generator" : "categorymembers",
                    "gcmtitle" : self.category,
                    "gcmprop" : "title",
                    "gcnamespace" : "6",
                    "gcmlimit" : "max",
                })))
        dic = result[u'query'][u'pages']
        list = sorted(dic.iteritems(), reverse=False, key=operator.itemgetter(1))
        liste2 = [x[1][u'categories'] for x in list if u'categories' in x[1].keys()]
        resu = set()
        for l in liste2:
            resu.update([x[u'title'] for x in l])
        return resu

    def first_image(self, category):
        self.catsql = category[9:].replace(" ", "_")
        self.cursor.execute(self.query, self.catsql)
        cat_content = self.catsql.encode('utf-8')
        first_content = [x[0].decode('utf-8') for x in self.cursor.fetchall()]
        res = {'cat': cat_content, 'first': first_content}
  #      print res
        return res

    def list_images(self):
        import os.path
        cache_name = "cache/%s.cache" % (self.category)
        result = json.loads(self.commons.send_to_api(mw_api.MwApiQuery(
                properties={
                    "list"         : "categorymembers",
                    "cmtitle"      : self.category,
                    "cmprop"       : "title",
                    "cmlimit"      : "max",
                })))
 #       print self.category 
        res1 = [x[u'title'] for x in result[u'query'][u'categorymembers']]
        res = [x.encode('utf-8') for x in res1]
 #       print "List of images"
 #       print res
	return res

def main():
    from argparse import ArgumentParser
    description = "Computes metrics about a commons category"
    parser = ArgumentParser(description=description)
    parser.add_argument("-c", "--category",
        type=str,
        dest="category",
        metavar="CAT",
        required=True,
        help="The category on which we compute metrics")
    args = parser.parse_args()
    ci = CategoryInduced(mw_util.str2cat(args.category))
    ci.categories = ci.list_category()
    first_images = [ci.first_image(x) for x in ci.categories]
    print "--------------------first images--------------------"
    print first_images
    images = [x.decode('utf-8')[5:] for x in ci.list_images()]
    print "----------------------images------------------------"
    print images
    result = [first_images[x]['cat'] for x in range(len(first_images)) if first_images[x]['first'][0] in images]
    print "----------------------result------------------------"
    print first_images[1]['first'][0].encode('utf-8')
    print first_images[1]['first'][0].encode('utf-8') in images
    print result

if __name__ == "__main__":
    main()
