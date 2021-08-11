import pandas as pd
import json
import os
from urllib.request import urlretrieve
from sklearn.model_selection import train_test_split




class ImageScraper:
    
    def __init__(self, file_path='../data/brick_insight_data/', file_size = 400, theme_data='../data/themes.csv', set_data='../data/sets.csv', save_images_folder='../data/image_data/') -> None:
        self.info_df = pd.DataFrame([])
        self.file_path = file_path
        self.file_size = file_size
        self.theme_data = pd.read_csv(theme_data)  # Load in the theme data
        self.theme_data['parent_id'].fillna(self.theme_data['id'], inplace=True ) # Fill NaNs in parent_id with theme
        self.theme_data['parent_id'] = self.theme_data['parent_id'].astype(int)
        self.set_data = pd.read_csv(set_data)[['set_num', 'theme_id']]  # Load in the set data
        self.save_images_folder = save_images_folder
        
        self.training_data = None
        self.testing_data = None


    def load_info(self):
        ''' 
        Loads in Lego data,
        drops columns that are not needed,
        and stores data as a pandas dataframe object in self.info_df 
        '''
        file_paths = os.listdir(self.file_path)
        for file in file_paths:
            with open(self.file_path + file) as f:
                data = json.load(f)
            current_df = pd.json_normalize(data)
            self.info_df = pd.concat([self.info_df, current_df])
        if self.file_size == 400:
            self.info_df = self.info_df[['set_id', 'name', 'image_urls.genericnx400']]

        elif self.file_size == 200:
            self.info_df = self.info_df[['set_id', 'name', 'image_urls.generic200xn']]

        elif self.file_size == 140:
            self.info_df = self.info_df[['set_id', 'name', 'image_urls.generic140xn']]

        elif self.file_size == 'Original':
            self.info_df = self.info_df[['set_id', 'name', 'image_urls.original']]
        
        self.info_df = self.info_df.rename(columns={self.info_df.columns[-1]:'image_url'}) # Rename last column to 'image_url'
        
        self.info_df = self.info_df[self.info_df['image_url'] != ''] # Remove rows that do not have an image url

        self.info_df = self.info_df.merge(self.set_data, how='inner', left_on='set_id', right_on='set_num')
        self.info_df = self.info_df.merge(self.theme_data, how='inner', left_on='theme_id', right_on='id')
        self.info_df = self.info_df.merge(self.theme_data, how='inner', left_on='parent_id', right_on='id')
        self.info_df = self.info_df[['set_id', 'name_x', 'image_url', 'name']]
        self.info_df = self.info_df.rename(columns={'name_x':'set_name', 'name': 'parent_theme'})
        self.info_df['parent_theme'] = self.info_df['parent_theme'].str.replace(" ", "")

    def sep_train_test(self):
        X_train, _, _, _ = train_test_split(self.info_df, self.info_df)
        self.info_df['training'] = self.info_df['set_id'].isin(X_train['set_id'])
    
    def fetch_images(self, num_of_rows=-1):
        self.info_df = self.info_df[:num_of_rows]
        for ttsplit in ['train/', 'test/']:
            if not os.path.isdir(self.save_images_folder + ttsplit):
                os.mkdir(self.save_images_folder + ttsplit)
            for theme in self.info_df['parent_theme'].unique():
                if not os.path.isdir(self.save_images_folder + ttsplit + theme):
                    os.mkdir(self.save_images_folder + ttsplit + theme)
        counter = 0    
        for _, row in self.info_df.iterrows():
            
            if row['training']:
                ttsplit = 'train/'
            else:
                ttsplit = 'test/'
            file_path = f'{self.save_images_folder}{ttsplit}{row["parent_theme"]}/{row["set_id"]}.jpg'
            urlretrieve(f'https://brickinsights.com{row["image_url"]}', file_path)
            print(f'On index number: {counter}')
            counter += 1
            print(f'Completed {round((counter / len(self.info_df)) * 100, 2)}%')




        




        



        





if __name__ =='__main__':
    scraper = ImageScraper()
    scraper.load_info()
    scraper.sep_train_test()
    print(scraper.info_df)
    scraper.fetch_images()
    