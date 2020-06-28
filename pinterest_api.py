import requests
import json
import os
from time import sleep
from bs4 import BeautifulSoup

import key


class Pinterest():
	def __init__(self, title):
		self.title = title
		self.api = 'https://api.pinterest.com/v1/boards/hero719/{}/pins/'.format(title)
		self.params = '?access_token={}&'\
						'limit=100&'\
						'fields=id,'\
						'link,'\
						'image'.format(key.Pinterest_access_token)
		self.url = self.api + self.params
		self.json_data = {}
		self.json_shaped = {'data':[]}
	
	def get_data(self, url):
		json_data = self.json_data
		print('リクエスト投げる前のURL：' + url)
		if url:
			json_data = requests.get(url)
		self.json_data = json_data.json()
	
	def data_shaping(self, dict_num):
		json_data = self.json_data
		i = dict_num#前回のデータ番号lenで出力し保持してくれてる
		value_array = []
		#api_data['data']が98なら0~97がnに入る
		for n in range(len(json_data['data'])):
		#iは最初0~97(ループ数)でnumは1スタートnum98まで
			num = i + 1#iのおかげで何番目のデータなのかわかる
			img_url = json_data['data'][n]['image']['original']['url']
			link = json_data['data'][n]['link']#linkはimageと同じ階層
			value_array.append({'image':img_url, 'from':link, 'num':num})
			print('保存されるデータ')
			print({'image':img_url, 'from':link, 'num':num})
			i += 1#何回ループしてるか計測

		#ループで作成した[{},{},{}...]リストデータを代入する。
		self.json_shaped['data'] = value_array

	def nextpage(self):
		json_data = self.json_data
		if 'page' in json_data:
			nextpage = json_data['page']['next']
			return nextpage
		return None
	
	def reverse_num(self, dict_pin_data):
		tmp = dict_pin_data
		n = 0
		l = len(tmp['data'])#何個データがあるか確認
		print(l)
		tmp_reversed = {'data':[]}#新しく作成ここに変換してデータを移し変える
		'''
		データ数からnを引いてnumに代入する事で番号を反転させる。
		num1番目を307(最後)に変えるなら307-0で代入2番目なら307-1
		で306になる
		'''
		for i in tmp['data']:#i = {'image':img_url, 'from':link, 'num':num}
			i['num'] = l - n
			n += 1
			tmp_reversed['data'].append(i)
		return tmp_reversed
	
	def get_redirect(self, redirect_url):
		
		try:
			r = requests.get(redirect_url)
			i = 0
			while 'www.pinterest' in redirect_url:
				if i > 20:
					print('これは20回やってもだめだった' + redirect_url)
					return redirect_url
				sleep(0.5)
				r = requests.get(redirect_url)
				print(r.url)
				redirect_url = r.url
				i += 1
		except requests.exceptions.ConnectionError as e:
			redirect_url = e.request.url
			print('リンク切れ' + redirect_url)
		done = 'これを保存' + redirect_url
		print(done)
		return redirect_url
	
	def confirm_redirect_url(self, redirect_url):
		check_url = redirect_url

		if 'www.pinterest' in check_url and '/pin/' in check_url and '/r/' not in check_url:
			r = requests.get(check_url)
			html = BeautifulSoup(r.text, 'html.parser')
			head = html.find('head')
			metatag = head.find('meta', attrs={'property':'og:see_also', 'content':True})
			if metatag['content']:
				check_url = metatag['content']

		return check_url
	
	def change_to_redirect_url(self, dict_pin_data):
		tmp = {'data':[]}
		for i in dict_pin_data['data']:#i = {'image':img_url, 'from':link, 'num':num}
			redirect_url = i['from']#linkのurl
			if redirect_url:
				got_url = self.get_redirect(redirect_url)
				checked_url = self.confirm_redirect_url(got_url)
				i['from'] = checked_url
			else:#targetが空なら代わりに自分のページを代入
				i['from'] = 'https://www.pinterest.jp/hero719/'
			tmp['data'].append(i)

		return tmp
	
	def create_data(self, dict_pin_data):
		path = os.getcwd()
		directory = path + '/json'
		os.makedirs(directory, exist_ok=True)
		with open(path + '/json/{}.json'.format(self.title), 'w') as f:
			json.dump(dict_pin_data, f)
	
	def store_img(self, dict_pin_data):
		
		for i in dict_pin_data['data']:
			print(i['image'])
			root, ext = os.path.splitext(i['image'])
			file_name = str(i['num']) + ext
			sleep(2)
			res = requests.get(i['image'], stream=True)
			path = os.getcwd()
			directory = path + '/img/{}'.format(self.title)
			os.makedirs(directory, exist_ok=True)
			with open(directory + '/' + file_name, 'wb') as img:#wbは書き込みをバイナリ（テキスト以外）で行うという意味
				for chunk in res.iter_content(chunk_size=1024):#chunkは大きいデータをメモリに一括でダウンロードしないようにする。
							img.write(chunk)
	
	def download(self):
		#apiにアクセスするURLを作成
		url = self.url
		json_shaped = self.json_shaped
		#ループするたびにdict_mydata,dict_numの値が加算されてく
		dict_pin_data = {'data':[]}
		dict_num = 0
		
		while url:
			print(url)
			sleep(3)
			#最初はデータ0のためdict_numには0が入る。
			dict_num = len(dict_pin_data['data'])
			print('while内のdict_num'+ str(dict_num))
			print(dict_pin_data)
			#pinterestのapiから帰ってきたデータを変数に保存して置く
			self.get_data(url)
			#使うデータだけ取り出してdict_tmpに保存numはデータに番号を振る
			self.data_shaping(dict_num)
			#dict_tmpには99件(最大で)のデータしか入ってないのでそれを前回のものに追加
			dict_pin_data['data'].extend(self.json_shaped['data'])
			#100件超えてデータが欲しい時apiに次のURLが載っているのでそれをurl変数に渡す
			url = self.nextpage()
		
		#できたデータの番号をひっくり返し更新しやすいようにする。
		dict_pin_data = self.reverse_num(dict_pin_data)
		#linkのURLをリダイレク先のURLに変更
		dict_pin_data = self.change_to_redirect_url(dict_pin_data)
		#dict_mydataをJsonで書き出す
		self.create_data(dict_pin_data)
		#データから画像をDL
		self.store_img(dict_pin_data)

#欲しいボードの名前を入力すれば取得できるよ
Pinterest = Pinterest('ファッションレディース')
Pinterest.download()