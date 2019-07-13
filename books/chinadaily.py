#!/usr/bin/env python
# -*- coding:utf-8 -*-

from datetime import datetime # ����ʱ�䴦��ģ��datetime
from base import BaseFeedBook # �̳л���BaseFeedBook
from lib.urlopener import URLOpener # ��������URL��ȡҳ�����ݵ�ģ��
from bs4 import BeautifulSoup # ����BeautifulSoup����ģ��

# ���ش˽ű����������
def getBook():
    return ChinaDaily

# �̳л���BaseFeedBook
class ChinaDaily(BaseFeedBook):
    # �趨���ɵ������Ԫ����
    title = u'China Daily' # �趨����
    __author__ = u'China Daily' # �趨����
    description = u'Chinadaily.com.cn is the largest English portal in China. ' # �趨���
    language = 'en' # �趨����

    coverfile = 'cv_chinadaily.jpg' # �趨����ͼƬ
    mastheadfile = 'mh_chinadaily.gif' # �趨��ͷͼƬ

    # ָ��Ҫ��ȡ�İ��������б������ҳ������
    # ÿ�������ǰ���������������ҳ�����ӵ�Ԫ��
    feeds = [
        (u'National affairs', 'http://www.chinadaily.com.cn/china/governmentandpolicy'),
        (u'Society', 'http://www.chinadaily.com.cn/china/society'),
    ]

    page_encoding = 'utf-8' # �趨��ץȡҳ���ҳ�����
    fulltext_by_readability = False # �趨�ֶ�������ҳ

    # �趨����ҳ��Ҫ�����ı�ǩ
    keep_only_tags = [
        dict(name='span', class_='info_l'),
        dict(name='div', id='Content'),
    ]

    max_articles_per_feed = 40 # �趨ÿ��������Ҫ����ץȡ����������
    oldest_article = 1 # �趨���µ�ʱ�䷶Χ��С�ڵ���365��λΪ�죬����λΪ�룬0Ϊ�����ơ�

    # ��ȡÿ������ҳ������������URL
    def ParseFeedUrls(self):
        urls = [] # ����һ���յ��б������������Ԫ��
        # ѭ������fees����������ҳ��
        for feed in self.feeds:
            # �ֱ��ȡԪ������������ƺ�����
            topic, url = feed[0], feed[1]
            # �ѳ�ȡÿ������ҳ���������ӵ����񽻸��Զ��庯��ParsePageContent()
            self.ParsePageContent(topic, url, urls, count=0)
        print urls
        exit(0)
        # ������ȡ�������������б�
        return urls

    # ���Զ��庯�����𵥸������������������ӵĳ�ȡ�����з�ҳ�����������һҳ
    def ParsePageContent(self, topic, url, urls, count):
        # ��������ҳ�����Ӳ���ȡ������
        result = self.GetResponseContent(url)
        # �������ɹ�������ҳ�����ݲ�Ϊ��
        if result.status_code == 200 and result.content:
            # ��ҳ������ת����BeatifulSoup����
            soup = BeautifulSoup(result.content, 'lxml')
            # �ҳ���ǰҳ�������б�������������Ŀ
            items = soup.find_all(name='span', class_='tw3_01_2_t')

            # ѭ������ÿ��������Ŀ
            for item in items:
                title = item.a.string # ��ȡ���±���
                link = item.a.get('href') # ��ȡ��������
                link = BaseFeedBook.urljoin(url, link) # �ϳ���������
                count += 1 # ͳ�Ƶ�ǰ�Ѵ����������Ŀ
                # ��������������Ŀ�������趨��������ֹ��ȡ
                if count > self.max_articles_per_feed:
                    break
                # ������·������ڳ������趨��Χ����Բ�����
                if self.OutTimeRange(item):
                    continue
                # �������趨����������ʱ�䷶Χ��������Ϣ��ΪԪ������б�
                urls.append((topic, title, link, None))

            # �������ҳ������һҳ�����Ѵ����������Ŀδ�����趨�����������ץȡ��һҳ
            next = soup.find(name='a', string='Next')
            if next and count < self.max_articles_per_feed:
                url = BaseFeedBook.urljoin(url, next.get('href'))
                self.ParsePageContent(topic, url, urls, count)
        # �������ʧ�����ӡ����־�����
        else:
            self.log.warn('Fetch article failed(%s):%s' % \
                (URLOpener.CodeMap(result.status_code), url))

    # �˺��������ж������Ƿ񳬳�ָ��ʱ�䷶Χ���Ƿ��� True�����򷵻�False
    def OutTimeRange(self, item):
        current = datetime.utcnow() # ��ȡ��ǰʱ��
        updated = item.find(name='b').string # ��ȡ���µķ���ʱ��
        # ����趨��ʱ�䷶Χ�����һ�ȡ�������·���ʱ��
        if self.oldest_article > 0 and updated:
            # �����·���ʱ���ַ���ת�������ڶ���
            updated = datetime.strptime(updated, '%Y-%m-%d %H:%M')
            delta = current - updated # ��ǰʱ���ȥ���·���ʱ��
            # ���趨��ʱ�䷶Χת�����룬С�ڵ���365��λΪ�죬������λΪ��
            if self.oldest_article > 365:
                threshold = self.oldest_article # ����Ϊ��λ��ֱ��ʹ����
            else:
                threshold = 86400 * self.oldest_article # ����Ϊ��λ��ת��Ϊ��
            # ������·���ʱ�䳬���趨ʱ�䷶Χ����True
            if (threshold < delta.days * 86400 + delta.seconds):
                return True
        # ����趨ʱ�䷶ΧΪ0������û�����趨ʱ�䷶Χ����û�з���ʱ�䣩���򷵻�False
        return False

    # ���Զ��庯���������󴫸��������Ӳ�������Ӧ����
    def GetResponseContent(self, url):
        opener = URLOpener(self.host, timeout=self.timeout, headers=self.extra_header)
        return opener.open(url)