import kivy
kivy.require('2.1.0')

from kivy.config import Config

#Config.set('graphics', 'width', 1080)
#Config.set('graphics', 'height', 2340)
#Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # eliminate annoying circle drawing on right click

from kivy.lang import Builder
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from functools import partial
from kivy.clock import Clock
##from kivy.resources import resource_add_path, resource_find
from database import DataBase 
import string
import random
import os
import time

Builder.load_file('kvFiles/main_store_window.kv')
Builder.load_file('kvFiles/each_item_box_template.kv')

Builder.load_file('kvFiles/adding_new_item_window.kv')

Builder.load_file('kvFiles/updating_item_details_window.kv')
Builder.load_file('kvFiles/item_details_update_template.kv')
Builder.load_file('kvFiles/show_item_details_template.kv')

Builder.load_file('kvFiles/delete_item_template.kv')

NoCamera = True
try:
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.INTERNET,
        Permission.CAMERA,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_EXTERNAL_STORAGE,
    ])
    Builder.load_file('kvFiles/camera_window.kv')
    NoCamera = False
except:
    pass

DataBaseFile = 'StoreData.db'
db = DataBase(DataBaseFile)


class ItemBoxTemplate(BoxLayout):
    def buttonAddClicked(self, item_id, new_item_numbers):
        updated_item_numbers = db.update_item_count(item_id, new_item_numbers, action='Add')
        self.ids.item_number.text = str(updated_item_numbers)

    def buttonDeleteClicked(self, item_id, new_item_numbers):
        updated_item_numbers = db.update_item_count(item_id, new_item_numbers, action='Delete')
        self.ids.item_number.text = str(updated_item_numbers)
        

class MainStoreWindow(Screen):
    
    def ItemBox(self):
        self.items = db.ReturnAllItems()
        if self.items:
            self.ShowItemTemplates()

    def ShowItemTemplates(self):
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        self.ids['items_grid_layout'] = layout
        for item in self.items:
            InstantItemBoxTemplate = ItemBoxTemplate()
            InstantItemBoxTemplate.ids.item_id.text = item[0]
            InstantItemBoxTemplate.ids.item_name.text = item[1]
            InstantItemBoxTemplate.ids.item_number.text = str(item[2])
            InstantItemBoxTemplate.ids.item_cost.text = str(item[3])
            InstantItemBoxTemplate.ids.image.source = item[4]
            layout.add_widget(InstantItemBoxTemplate)
        self.ids.item_scroll.add_widget(layout)

    def RemoveItemTemplates(self):
        if self.items: self.ids.item_scroll.remove_widget(self.ids.items_grid_layout)

    def AddItemBtn(self):
        self.RemoveItemTemplates()
        sm.current = 'new_item_add'

    def DetailsUpdateScreen(self):
        self.RemoveItemTemplates()
        sm.get_screen('details_update').action = 'update'
        sm.get_screen('details_update').ids.update_item_window_.text = 'Update item details'
        sm.current = 'details_update'

    def DeleteItemScreen(self):
        self.RemoveItemTemplates()
        sm.get_screen('details_update').action = 'DELETE'
        sm.get_screen('details_update').ids.update_item_window_.text = 'Delete item'
        sm.current = 'details_update'

class TakePicture(Screen):

    def __init__(self, **kwargs):
        super(TakePicture, self).__init__(**kwargs)
        self.which_window = 'new_item_add'

    def SaveImage(self):
        timestr = time.strftime("%Y%m%d_%H%M%S")
        self.image_pathh = os.path.join(App.get_running_app().storage_path, "IMG_{}.jpg".format(timestr))
        iimg = self.ids.camera_img.export_as_image()
        iimg.save(self.image_pathh)
        ##self.ids.camera_img.export_to_png(self.image_pathh)
        self.NewImagePathUpdate(self.which_window)

    def NewImagePathUpdate(self, which_window_):
        all_ids_in_path = sm.get_screen(which_window_).ids
        if which_window_ == 'details_update': all_ids_in_path = all_ids_in_path.update_item_box_template.ids
        all_ids_in_path.image_path.text = self.image_pathh
        all_ids_in_path.image_path.disabled = True
        self.ReturnBack()

    def ReturnBack(self):
        self.ids.camera_img.play = not self.ids.camera_img.play
        sm.current = self.which_window


class AddItemWindow(Screen):
    item_namee = ObjectProperty()
    item_id = ObjectProperty()
    item_number = ObjectProperty()
    item_cost = ObjectProperty()
    image = ObjectProperty()

    def __init__(self, **kwargs):
        super(AddItemWindow, self).__init__(**kwargs)
        self.ItemList = []
        self.ItemListIds = []

    def GenerateRandomId(self):
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        size = random.randint(2, 6)
        RandomID =  ''.join(random.choice(chars) for _ in range(size))
        self.ids.item_id.text = RandomID
            

    def CameraClick(self):
        if NoCamera:
            WrongItemPopUp('Need camera permission. Enable camera permission from phone settings for this app.')
            self.ids.camera_take_picture.disabled = True
        else:
            sm.current = 'take_picture'

    def CheckLength_name(self, max_length = 10):
        if len(self.ids.item_name.text.strip()) > max_length:
            WrongItemPopUp(f'Maximum {max_length} charachter allowed.')
            self.ids.item_name.do_undo()

    def CheckLength_id(self, max_length = 6):
        if len(self.ids.item_id.text.strip()) > max_length:
            WrongItemPopUp(f'Maximum {max_length} charachter allowed.')
            self.ids.item_id.do_undo()

    def CheckItemsEligibility(self):
        item_id, item_name, item_numbers, item_cost, item_img_path = \
        self.item_id.text.strip(), self.item_namee.text.strip(), self.item_number.text.strip(),\
        self.item_cost.text.strip(), self.image.text.strip()

        check_item_id_database = db.check_item_eligibility(item_id)

        if not item_id:
            WrongItemPopUp('Item id is mandatory. Please supply an appropriate unique item id.')
            return False
        if not item_name:
            WrongItemPopUp('Item name is mandatory. Please supply an appropriate item name.')
            return False
        if not item_numbers: item_numbers = '0'
        if not item_img_path: item_img_path = 'imgs/test.jpg'
        if not item_cost: item_cost = '0'
        try:
            item_numbers = int(item_numbers)
            item_cost = float(item_cost)
        except:
            WrongItemPopUp('Item count and cost should be number.')
            return False
        if item_img_path.split('.')[-1] not in ['png', 'jpg']:
            WrongItemPopUp('Only png and jpeg image are allowed.')
            return False

        if check_item_id_database or (item_id in self.ItemListIds):
            WrongItemPopUp('Item id already exists. Please supply new id.')
            return False
        else:
            #print(self.ItemList)
            self.check_new_item = (item_id, item_name, item_numbers, item_cost, item_img_path)
            self.ItemList.append(self.check_new_item)
            self.ItemListIds.append(item_id)
            self.reset()
        return True

    def Submit(self):
        if len(self.ItemList) > 0:
            db.add_new_items(self.ItemList)
            self.ReturnBack()
            return
        else:
            WrongItemPopUp('Click on "Add to bucket" and then "Save".')
        return 


    def ReturnBack(self):
        self.ItemList = []
        self.ItemListIds = []
        self.reset()
        sm.current = "all_items"
        self.ids.add_item_label_box.clear_widgets()

    def reset(self):
        self.item_id.text = ''
        self.item_namee.text = ''
        self.item_number.text = '0'
        self.item_cost.text = '0'
        self.image.text = 'imgs/test.jpg'
        self.image.disabled = False
        self.ids.camera_take_picture.disabled = False

    def AddItemWidget(self):
        # https://stackoverflow.com/a/61707198
        scroll_vp_height = self.ids.add_item_label.viewport_size[1]
        scroll_height = self.ids.add_item_label.height

        label = AddItemWidgetLabel() 
        label.text = '        '+ self.check_new_item[0] + ':  ' + self.check_new_item[1] 
        self.ids.add_item_label_box.add_widget(label)
        
        if scroll_vp_height > scroll_height:
            scroll_fact = self.ids.add_item_label.scroll_y
            bottom = scroll_fact * (scroll_vp_height-scroll_height)
            Clock.schedule_once(partial(self.adjust_scroll, bottom+label.height))

    def adjust_scroll(self, bottom, dt):
        scroll_vp_height = self.ids.add_item_label.viewport_size[1]
        scroll_height = self.ids.add_item_label.height
        self.ids.add_item_label.scroll_y = bottom / (scroll_vp_height-scroll_height)

class AddItemWidgetLabel(Label):
    pass

class UpdateItemBoxTemplate(GridLayout):
    pass


class UpdateItemProperties(BoxLayout):
    def __init__(self, item):
        super(UpdateItemProperties, self).__init__()
        self.updated_item = list(item)
        self.save_and_back = False

    def UpdateCostDataBase(self, new_cost):
        if new_cost and new_cost.strip():
            try:
                self.updated_item[3] = float(new_cost)
                self.save_and_back = True
            except:
                WrongItemPopUp('Item cost should be number.')
                self.ids.update_item_cost_new.text = ''
                return 0
        return 1

    def UpdateDataBase_for_Item(self, new_name, new_image):
        if new_name and new_name.strip(): 
            self.updated_item[1] = new_name.strip() 
            self.save_and_back = True

        if new_image and new_image.strip(): 
            self.updated_item[4] = new_image.strip()
            self.save_and_back = True

        if self.save_and_back:
            db.UpdateNewItemDetails(tuple(map(self.updated_item.__getitem__, [1, 3, 4, 0])))
            self.ReturnBack()
        else:
            WrongItemPopUp('Nothing to save.')


    def DeleteOldScreen(self):
        old_template = sm.get_screen('details_update').ids.update_box_template
        sm.get_screen('details_update').ids.update_item_scroll.remove_widget(old_template)
        sm.get_screen('details_update').ids.update_item_id_row.disabled = False
        self.ids.camera_take_picture.disabled = False
        sm.get_screen('details_update').ids.update_item_id.text = 'None'
        self.save_and_back = False

    def CameraClick(self):
        if NoCamera:
            WrongItemPopUp('Need camera permission. Enable camera permission from phone settings for this app.')
            self.ids.camera_take_picture.disabled = True
        else:
            sm.get_screen('take_picture').which_window = 'details_update'
            sm.current = 'take_picture'

    def RefreshBack(self):
        self.DeleteOldScreen()

    def ReturnBack(self):
        self.DeleteOldScreen()
        sm.current = 'all_items'

class DeleteItem(BoxLayout):
    def __init__(self, item):
        super(DeleteItem, self).__init__()
        self.itemm = item

    def DeleteItemDataBase(self):
        if self.itemm[4] != 'imgs/test.jpg' and self.itemm[4] != 'imgs/presplash.png':
            try:
                os.remove(self.itemm[4])
            except:
                WrongItemPopUp("Can't delete image.")
                return
        db.DeleteItem(self.itemm[0])
        WrongItemPopUp("Delete sucessful.")
        self.RefreshButton()
        sm.get_screen('details_update').ids.update_item_id.values = db.id_list()
        return

    def DeleteOldScreen(self):
        old_template = sm.get_screen('details_update').ids.update_box_template
        sm.get_screen('details_update').ids.update_item_scroll.remove_widget(old_template)
        sm.get_screen('details_update').ids.update_item_id_row.disabled = False
        sm.get_screen('details_update').ids.update_item_id.text = 'None'

    def RefreshButton(self):
        self.DeleteOldScreen()

    def ReturnBack(self):
        self.DeleteOldScreen()
        sm.current = 'all_items'

class UpdateItemDetails(Screen):
    update_item_id = ObjectProperty()
    action = StringProperty()

    def ID_list(self):
        self.update_item_id.values = db.id_list()
        return 

    def get_item_details(self):
        self.item_id = self.update_item_id.text 
        if self.item_id and self.item_id.strip():
            self.item = db.get_item_properties(self.item_id.strip())
            if self.item is None: 
                WrongItemPopUp('Item id does not exist.')
                return 0
        else:
            WrongItemPopUp('Please supply the item id.')
            return 0
        self.ids.update_item_id_row.disabled = True
        return 1

    def DeleteMyItem(self):
        llayout = DeleteItem(item=self.item) 
        return llayout
    
    def UpdateMyItem(self):
        llayout = UpdateItemProperties(item=self.item)
        return llayout

    def ShowItemDetails(self, action):
        layout = UpdateItemBoxTemplate()
        self.ids['update_box_template'] = layout
        layout.ids.update_item_id.text = self.item[0]
        layout.ids.update_item_name.text = self.item[1]
        layout.ids.update_item_number.text = str(self.item[2])
        layout.ids.update_item_cost.text = str(self.item[3])
        layout.ids.update_image.source = self.item[4]

        SpecificLayout = self.UpdateMyItem() if action == 'update' else self.DeleteMyItem()
        self.ids['update_item_box_template'] = SpecificLayout 
        layout.add_widget(SpecificLayout)

        self.ids.update_item_scroll.add_widget(layout)
    
    def ReturnBack(self):
        self.ids.update_item_id_row.disabled = False
        self.update_item_id.text = 'None'
        sm.current = 'all_items'

def WrongItemPopUp(popup_text):
    content = Button(text='Close',
                    size_hint_y=0.1) 
    pop = Popup(title=popup_text,
                  content=content,
                  size_hint=(0.5,0.5),
                  auto_dismiss = True)
    content.bind(on_press=pop.dismiss)

    pop.open()

class WindowManager(ScreenManager):
    pass

sm = WindowManager()

screens = [MainStoreWindow(name="all_items"), AddItemWindow(name='new_item_add'), UpdateItemDetails(name='details_update'), \
        TakePicture(name='take_picture')]
for screen in screens:
    sm.add_widget(screen)

class InventoryManagerApp(App):
    def __init__(self, **kwargs):
        super(InventoryManagerApp, self).__init__(**kwargs)

    @property
    def storage_path(self):
        return self.user_data_dir
    
    def build(self):
        return sm

if __name__ == '__main__':
    __version__ = '0.1'
    InventoryManagerApp().run()
