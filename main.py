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
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.settings import SettingsWithSpinner, SettingPath
from functools import partial
from kivy.clock import Clock
from kivy.utils import platform
##from kivy.resources import resource_add_path, resource_find
from database import DataBase, CustomerDataBase 
from update_settings import  update_settings
from update_settings_string_path import  update_settings as update_settings_string_path
import string
import random
import os
import time
import gc
from fpdf import FPDF

Builder.load_file('kvFiles/heading.kv')
Builder.load_file('kvFiles/previous_screen.kv')
Builder.load_file('kvFiles/help_page.kv')

Builder.load_file('kvFiles/main_store_window.kv')
Builder.load_file('kvFiles/each_item_box_template.kv')

Builder.load_file('kvFiles/adding_new_item_window.kv')

Builder.load_file('kvFiles/updating_item_details_window.kv')

Builder.load_file('kvFiles/customer_info.kv')
Builder.load_file('kvFiles/customer_checkout.kv')

Builder.load_file('kvFiles/filechooser.kv')

NoCamera = True
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.INTERNET,
        Permission.CAMERA,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_EXTERNAL_STORAGE,
    ])
    NoCamera = False

if not NoCamera: Builder.load_file('kvFiles/camera_window.kv')

class Heading(BoxLayout):
    def __init__(self, sm, **kwargs):
        super(Heading, self).__init__(**kwargs)
        self.sm = sm

    def GoToHelp(self):
        self.sm.current_screen.HelpPage()
    

chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
def RandomId(max_limit=6, min_limit=2):
    size = random.randint(min_limit, max_limit)
    return ''.join(random.choice(chars) for _ in range(size))

def WrongItemPopUp(popup_text):
    content = Button(text='Close',
                    size_hint_y=0.1) 
    pop = Popup(title=popup_text,
                  content=content,
                  size_hint=(0.5,0.5),
                  auto_dismiss = True)
    content.bind(on_press=pop.dismiss)

    pop.open()

# https://stackoverflow.com/a/59805349
class Chooser(TextInput):
    choiceslist = ListProperty([])

    def __init__(self, sm, **kwargs):
        self.choiceslist = kwargs.pop('choiceslist', [])  # list of choices
        super(Chooser, self).__init__(**kwargs)
        self.multiline = False
        self.cursor_color = [0,0,0,1]
        self.size_hint = (0.9, 0.9)
        self.halign = 'left'
        self.bind(text=self.on_text)
        self.bind(focus=self.on_focus)
        self.dropdown = None
        self.suggestion_text = None
        self.sm = sm

    def open_dropdown(self, *args):
        if self.dropdown:
            self.dropdown.open(self)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if self.suggestion_text and keycode[0] == ord('\r'):  # enter selects current suggestion
            self.suggestion_text = ' '  # setting suggestion_text to '' screws everything
            self.text = self.values[0]
            if self.dropdown:
                self.dropdown.dismiss()
                self.dropdown = None
        else:
            super(Chooser, self).keyboard_on_key_down(window, keycode, text, modifiers)

    def on_focus(self, instance, text):
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None
        self.dropdown = DropDown()
        for val in self.choiceslist:
            self.dropdown.add_widget(Button(text=val[0], size_hint_y=None, height=48, on_release=partial(self.do_choose, val[1])))
        self.dropdown.open(self)

    def on_text(self, chooser, text):
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None
        if text == '':
            return
        values = []
        for addr in self.choiceslist:
            if addr[0].startswith(text):
                values.append(addr)
        self.values = values
        if len(values) > 0:
            if len(self.text) < len(self.values[0][0]):
                self.suggestion_text = self.values[0][0][len(self.text):]
            else:
                self.suggestion_text = ' '  # setting suggestion_text to '' screws everything
            self.dropdown = DropDown()
            for val in self.values:
                self.dropdown.add_widget(Button(text=val[0], size_hint_y=None, height=48, on_release=partial(self.do_choose, val[1])))
            self.dropdown.open(self)

    def do_choose(self, butt, instancee):
        self.text = butt
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None
        self.sm.current_screen.ShowItemDetails()

class ItemBoxTemplate(BoxLayout):
    def __init__(self,db,sm,**kwargs):
        super(ItemBoxTemplate, self).__init__(**kwargs)
        self.db = db
        self.sm = sm

    def PopupCallBack(self, instance):
        self.db.DeleteItem(self.ids.item_id.text)
        self.parent.remove_widget(self)

    def PopUp(self, popup_text):
        content = SetCustomerPopupBox()  
        pop = Popup(title=popup_text,
                      content=content,
                      size_hint=(0.5,0.5),
                      auto_dismiss = False)
        content.ids.CustomerPopupBox_btn1.bind(on_press=self.PopupCallBack)
        content.ids.CustomerPopupBox_btn1.bind(on_release=pop.dismiss)
        content.ids.CustomerPopupBox_btn2.bind(on_release=pop.dismiss)
        pop.open()
        return

    def RemoveItem(self):
        tmp_image_path = self.ids.image.source
        if tmp_image_path != 'imgs/test.jpg':
            try:
                os.remove(tmp_image_path)
            except:
                self.PopUp("Can't delete image. Do you want to force delete?")
                return
        self.db.DeleteItem(self.ids.item_id.text)
        self.parent.remove_widget(self)
        self.sm.current_screen.ids.choose_item_id.choiceslist = self.db.id_list()
        return

    def ValidateEnteredItemNumber(self, new_item_numbers):
        try:
            new_item_numbers = int(new_item_numbers) if new_item_numbers is not None and len(new_item_numbers.strip())>0 else 0
        except:
            WrongItemPopUp("Count can't be fraction.")
            return 0
        if new_item_numbers < 0: WrongItemPopUp("Only positive number is allowed.")

        return new_item_numbers

    def CheckNegativeCount(self):
        if self.CheckCountNegative:
            WrongItemPopUp("Item stock already empty.")
        else:
            self.db.update_item_count(self.ids.item_id.text, self.updated_item_numbers)
            self.ids.item_number.text = str(self.updated_item_numbers)
        return 1

    def buttonAddClicked(self, item_id, new_item_numbers):
        new_item_numbers = self.ValidateEnteredItemNumber(new_item_numbers)
        if new_item_numbers > 0:
            self.updated_item_numbers, self.CheckCountNegative = self.db.validate_item_count(item_id, new_item_numbers, action='Add')
            self.CheckNegativeCount() 
            self.ids.NumberOfItems.text = '1'

    def buttonDeleteClicked(self, item_id, new_item_numbers):
        new_item_numbers = self.ValidateEnteredItemNumber(new_item_numbers)
        if new_item_numbers > 0:
            self.updated_item_numbers, self.CheckCountNegative = self.db.validate_item_count(item_id, new_item_numbers, action='Delete')
            self.CheckNegativeCount()
            self.ids.NumberOfItems.text = '1'
        
    def DetailsUpdateScreen(self):
        get_screen_ids = self.sm.get_screen('details_update').ids
        get_screen_ids.update_item_window_.text = 'Update item details'
        get_screen_ids.update_item_remove_btn.disabled = True 
        get_screen_ids.update_item_save_btn.disabled = False
        self.sm.current = 'details_update'
        get_screen_ids.choose_item_id.text = self.ids.item_id.text
        get_screen_ids.choose_item_id_box_id.disabled = True
        get_screen_ids.update_item_details_data_box.disabled = False
        #self.sm.current_screen.ShowItemDetails()
        item = self.db.get_item_properties(self.ids.item_id.text)
        get_screen_ids.update_item_name.text = item[1]
        get_screen_ids.update_item_number.text = str(item[2])
        get_screen_ids.update_item_cost.text = str(item[3])
        get_screen_ids.update_image.source = item[4]

class TakePicture(Screen):

    def __init__(self, sm, **kwargs):
        super(TakePicture, self).__init__(**kwargs)
        self.which_window = 'new_item_add'
        self.sm = sm

    def SaveImage(self):
        timestr = time.strftime("%Y%m%d_%H%M%S")
        self.image_pathh = os.path.join(App.get_running_app().image_storage_path, "IMG_{}.jpg".format(timestr))
        iimg = self.ids.camera_img.export_as_image()
        iimg.save(self.image_pathh)
        ##self.ids.camera_img.export_to_png(self.image_pathh)
        self.NewImagePathUpdate(self.which_window)

    def NewImagePathUpdate(self, which_window_):
        all_ids_in_path = self.sm.get_screen(which_window_).ids
        #if which_window_ == 'details_update': all_ids_in_path = all_ids_in_path.update_item_box_template.ids
        all_ids_in_path.image_path.text = self.image_pathh
        all_ids_in_path.image_path.disabled = True
        self.ReturnBack()

    def ReturnBack(self):
        self.ids.camera_img.play = False 
        self.sm.current = self.which_window
        self.sm.current_screen.ids.image_path.focus = not self.sm.current_screen.ids.image_path.focus

class Filechooser(BoxLayout):
    def __init__(self, **kwargs):
        super(Filechooser, self).__init__(**kwargs)
        self.ids.let_choose.path = '/storage/emulated/0/' if platform == 'android' else '.'

class LetsSelectFile:
    def __init__(self, sm, **kwargs):
        self.sm = sm

    def GetFilePath(self, filechooser, instance):
        filepath_select = filechooser.ids.let_choose.selection[0]
        self.sm.current_screen.ids.image_path.text = filepath_select
        self.sm.current_screen.ids.image_path.focus = not self.sm.current_screen.ids.image_path.focus

    def FileChooserClick(self):
        content = Filechooser()
        pop = Popup(title='Choose a file',
                      content=content,
                      size_hint=(0.9,0.8),
                      auto_dismiss = True)
        content.ids.close_btn.bind(on_release=pop.dismiss)
        content.ids.confirm_btn.bind(on_press=partial(self.GetFilePath, content))
        content.ids.confirm_btn.bind(on_release=pop.dismiss)
        pop.open()
        return 

class HelpPageScreen(Screen):
    def __init__(self,sm,**kwargs):
        super(HelpPageScreen, self).__init__(**kwargs)
        self.sm = sm
        self.ids.heading.add_widget(Heading(self.sm))

    def HelpPage(self):
        #sm.get_screen('help_page').ids.help_page.goto('additem')
        self.sm.current = 'help_page'

class MainStoreWindow(Screen):
    def __init__(self, db, sm, **kwargs):
        super(MainStoreWindow, self).__init__(**kwargs)
        self.db = db
        self.sm = sm
        self.ids.heading.add_widget(Heading(self.sm))

    def HelpPage(self):
        #sm.get_screen('help_page').ids.help_page.goto('additem')
        self.sm.current = 'help_page'

    def InitializeScreen(self):
        if 'choose_item_id' not in self.ids:
            chooser = Chooser(self.sm,choiceslist=self.db.id_list(), hint_text='enter item name/id', size_hint=(0.5,None), height=30, pos_hint={'center_x':0.5, 'center_y':0.5})
            self.ids.search_item_id.add_widget(chooser)
            self.ids['choose_item_id'] = chooser
        else:
            self.ids.choose_item_id.choiceslist = self.db.id_list()
            self.ids.choose_item_id.text = ''

    def ShowItemDetails(self):
        tmp_item_search = self.ids.choose_item_id.text.strip() + 'MainStore'
        self.ids.item_scroll.scroll_to(self.ids.items_grid_layout.ids[tmp_item_search])

    def AllItemGridLayout(self):
        self.layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.ids['items_grid_layout'] = self.layout
        self.ids.item_scroll.add_widget(self.layout)

    def ShowItemTemplates(self):
        self.AllItemGridLayout()
        for item in self.items:
            InstantItemBoxTemplate = ItemBoxTemplate(self.db, self.sm)
            self.layout.ids[item[0]+'MainStore'] = InstantItemBoxTemplate
            InstantItemBoxTemplate.ids.item_id.text = item[0]
            InstantItemBoxTemplate.ids.item_name.text = item[1]
            InstantItemBoxTemplate.ids.item_number.text = str(item[2])
            InstantItemBoxTemplate.ids.item_cost.text = str(item[3])
            InstantItemBoxTemplate.ids.image.source = item[4]
            self.layout.add_widget(InstantItemBoxTemplate)

    def AddItemBtn(self):
        self.sm.current = 'new_item_add'

    def DetailsUpdateScreen(self):
        get_screen_ids = self.sm.get_screen('details_update').ids
        get_screen_ids.update_item_window_.text = 'Update item details'
        get_screen_ids.update_item_remove_btn.disabled = True 
        get_screen_ids.update_item_refresh_btn.disabled = False 
        get_screen_ids.choose_item_id_box_id.disabled = False
        get_screen_ids.update_item_save_btn.disabled = False
        get_screen_ids.update_item_details_data_box.disabled = False
        self.sm.current = 'details_update'

    def DeleteItemScreen(self):
        get_screen_ids = self.sm.get_screen('details_update').ids
        get_screen_ids.update_item_window_.text = 'Delete item'
        get_screen_ids.update_item_save_btn.disabled = True 
        get_screen_ids.update_item_details_data_box.disabled = True
        get_screen_ids.update_item_remove_btn.disabled = False 
        get_screen_ids.update_item_refresh_btn.disabled = True
        self.sm.current = 'details_update'

    def PrintSummary(self):
        self.summary_items = self.db.ReturnAllItems()
        if self.summary_items:
            # Create a popup for orientation
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, txt='******** Welcome to Inventory Manager ********', ln=1, align='C')

            Header_list = ['ID', 'NAME', 'COUNT', 'COST', 'IMAGE']
            col_width = pdf.w / (float(len(Header_list)) + 0.5)
            spacing = 1.5
            row_height = pdf.font_size * spacing
            pdf.cell(0, 10, txt='-------- Summary of all items in stock ---------', ln=1, align='C')
            pdf.cell(0, 10, txt=time.strftime("%d-%m-%Y  %H:%M:%S"), ln=1, align='R')
            pdf.ln(row_height)

            pdf.cell(0, 10, txt='='*80, ln=1, align='C')
            for hdr_fld in Header_list:
                pdf.cell(col_width, row_height, txt=str(hdr_fld), border=0)
            pdf.ln(row_height)
            pdf.cell(0, 10, txt='='*80, ln=1, align='C')
            pdf.ln(row_height)

            for item in self.summary_items:
                for col in item:
                    tmp_txt = str(col) 
                    if len(tmp_txt)>8: tmp_txt = tmp_txt[:9] + '...'
                    pdf.cell(col_width, row_height, txt=tmp_txt, border=0)
                pdf.ln(row_height)
                #row_item = ''.join([str(col).strip().rjust(20) + " " for  col in item])
                #pdf.cell(0, 10, txt = row_item, ln=1, align='C')

            filepath_pdf = os.path.join(App.get_running_app().save_documents_dir, 'ItemsSummary_'+time.strftime("%Y%m%d_%H%M%S")+'.pdf')
            pdf.output(filepath_pdf)
            WrongItemPopUp(f"Items summary: {filepath_pdf}")
        else:
            WrongItemPopUp("No item exists.")

    def CustomerInfoPage(self):
        self.sm.current = 'customer_info'
        self.sm.current_screen.ids.checkout_button.disabled = True
        self.sm.current_screen.ids.checkout_back_button.disabled = True

    def CustomerCheckOut(self):
       self.sm.current = 'customer_checkout'


class AddItemWindow(Screen):
    item_namee = ObjectProperty()
    item_id = ObjectProperty()
    item_number = ObjectProperty()
    item_cost = ObjectProperty()
    image = ObjectProperty()

    def __init__(self, db, sm, **kwargs):
        super(AddItemWindow, self).__init__(**kwargs)
        self.ItemSummaryList = {}
        self.db = db
        self.sm = sm
        self.ids.heading.add_widget(Heading(self.sm))

    def HelpPage(self):
        self.sm.get_screen('help_page').ids.help_page.goto('additem')
        self.sm.current = 'help_page'

    def ID_list(self):
        self.item_id_list_db = self.db.id_list()
        return 

    def GenerateRandomId(self):
        self.ids.item_id.text = RandomId(min_limit=5, max_limit=20)

    def CameraClick(self):
        if NoCamera:
            WrongItemPopUp('Need camera permission. Enable camera permission from phone settings for this app.')
            self.ids.camera_take_picture.disabled = True
        else:
            self.sm.get_screen('take_picture').which_window = 'new_item_add'
            self.sm.current = 'take_picture'

    def CheckLength_name(self, max_length = 20):
        if len(self.ids.item_name.text.strip()) > max_length:
            WrongItemPopUp(f'Maximum {max_length} character allowed.')
            self.ids.item_name.do_undo()

    def CheckLength_id(self, max_length = 20):
        if len(self.ids.item_id.text.strip()) > max_length:
            WrongItemPopUp(f'Maximum {max_length} character allowed.')
            self.ids.item_id.do_undo()

    def CheckItemsEligibility(self):
        item_id, item_name, item_numbers, item_cost, item_img_path = \
        self.item_id.text.strip(), self.item_namee.text.strip(), self.item_number.text.strip(),\
        self.item_cost.text.strip(), self.image.text.strip()

        #check_item_id_database = True if item_id in self.item_id_list_db else False
        check_item_id_database = self.db.check_item_eligibility(item_id)

        if not item_id:
            WrongItemPopUp('Item id is mandatory. Supply an appropriate unique item id.')
            return 

        if check_item_id_database or (item_id+'ItemsAdded' in self.ItemSummaryList):
            WrongItemPopUp('Item id already exists. Provide new id.')
            return

        if not item_name:
            WrongItemPopUp('Item name is mandatory. Supply an appropriate item name.')
            return
        if item_img_path.startswith('imgs/app/'): 
            WrongItemPopUp('Not allowed path. Access denied. Path is reserved for default app images only.')
            return

        if not item_numbers: item_numbers = '0'
        if not item_img_path: item_img_path = 'imgs/test.jpg'
        if not item_cost: item_cost = '0'
        try:
            item_numbers = int(item_numbers)
            item_cost = float(item_cost)
        except:
            WrongItemPopUp('Item count and cost should be number.')
            return

        if item_img_path.split('.')[-1] not in ['png', 'jpg', 'jpeg']:
            WrongItemPopUp('Only png and jpeg images are allowed.')
            return

        check_new_item = (item_id, item_name, item_numbers, item_cost, item_img_path)
        KEY = check_new_item[0]+'ItemsAdded'
        self.ItemSummaryList[KEY] = check_new_item
        self.AddItemWidget(KEY)
        self.reset()
        return 

    def UpdateLists(self, myid): # This function is for AddItemWidgetLabelV2
        pass

    def Submit(self):
        if len(self.ItemSummaryList) > 0:
            self.db.add_new_items(list(self.ItemSummaryList.values()))
            self.add_new_item_widget_main_store()
            self.ReturnBack()
        else:
            WrongItemPopUp('Click on "Add to bucket" and then "Save".')
        return 

    def add_new_item_widget_main_store(self):
        get_all_items_screen_grid = self.sm.get_screen('all_items').ids.items_grid_layout
        for item_ii in self.ItemSummaryList:
            item_i = self.ItemSummaryList[item_ii]
            InstantItemBoxTemplate = ItemBoxTemplate(self.db, self.sm)
            InstantItemBoxTemplate.ids.item_id.text = item_i[0]
            InstantItemBoxTemplate.ids.item_name.text = item_i[1]
            InstantItemBoxTemplate.ids.item_number.text = str(item_i[2])
            InstantItemBoxTemplate.ids.item_cost.text = str(item_i[3])
            InstantItemBoxTemplate.ids.image.source = item_i[4]
            get_all_items_screen_grid.add_widget(InstantItemBoxTemplate)
            get_all_items_screen_grid.ids[item_i[0]+'MainStore'] = InstantItemBoxTemplate

    def ReturnBack(self):
        self.ItemSummaryList.clear()
        self.reset()
        self.sm.current = "all_items"
        self.ids.add_item_label_box.clear_widgets()

    def reset(self):
        self.item_id.text = ''
        self.item_namee.text = ''
        self.item_number.text = '0'
        self.item_cost.text = '0'
        self.image.text = ' '
        self.image.disabled = False
        self.ids.camera_take_picture.disabled = False
        self.ids.lets_choose_file.source = ''

    def CutTexts(self, txt, max_limit = 15):
        if len(txt) > max_limit: 
            txt  = txt[:max_limit+1] + '...'
        else:
            txt = txt + '  '*(18-len(txt)) 
        return txt

    def AddItemWidget(self, KEY):
        # https://stackoverflow.com/a/61707198
        scroll_vp_height = self.ids.add_item_label.viewport_size[1]
        scroll_height = self.ids.add_item_label.height

        label = AddItemWidgetLabelV2(self.sm) 
        label.my_id = KEY
        item = self.ItemSummaryList[KEY]
        label.ids.add_item_widget_label.text = self.CutTexts(item[0]) + ':  ' + self.CutTexts(item[1]) 
        self.ids.add_item_label_box.add_widget(label)
        
        if scroll_vp_height > scroll_height:
            scroll_fact = self.ids.add_item_label.scroll_y
            bottom = scroll_fact * (scroll_vp_height-scroll_height)
            Clock.schedule_once(partial(self.adjust_scroll, bottom+label.height))

    def adjust_scroll(self, bottom, dt):
        scroll_vp_height = self.ids.add_item_label.viewport_size[1]
        scroll_height = self.ids.add_item_label.height
        self.ids.add_item_label.scroll_y = bottom / (scroll_vp_height-scroll_height)

    def FileChooserClick(self):
        content = LetsSelectFile(self.sm)
        content.FileChooserClick()

class AddItemWidgetLabelV2(BoxLayout):
    def __init__(self, sm, **kwargs):
        super(AddItemWidgetLabelV2, self).__init__(**kwargs)
        self.sm = sm
    def CheckoutDeleteItemFromList(self):
        # Do not change the order. The function should be called exactly in this order.
        self.sm.current_screen.UpdateLists(self.my_id)
        self.sm.current_screen.ItemSummaryList.pop(self.my_id)
        self.parent.remove_widget(self)

class UpdateItemDetails(Screen):

    def __init__(self, db, sm, **kwargs):
        super(UpdateItemDetails, self).__init__(**kwargs)
        self.db = db
        self.sm = sm
        self.ids.heading.add_widget(Heading(self.sm))

    def HelpPage(self):
        self.sm.get_screen('help_page').ids.help_page.goto('additem')
        self.sm.current = 'help_page'

    def InitializeScreen(self):
        if 'choose_item_id' not in self.ids:
            chooser = Chooser(self.sm, choiceslist=self.db.id_list(), hint_text='enter item name/id', size_hint=(0.5,None), height=30, pos_hint={'center_x':0.5, 'center_y':0.5})
            self.ids.choose_item_id_.add_widget(chooser)
            self.ids['choose_item_id'] = chooser
        else:
            self.ids.choose_item_id.choiceslist = self.db.id_list()

    def FileChooserClick(self):
        content = LetsSelectFile(self.sm)
        content.FileChooserClick()

    def ShowItemDetails(self):
        item = self.db.get_item_properties(self.ids.choose_item_id.text.strip())
        self.ids.update_item_name.text = item[1]
        self.ids.update_item_number.text = str(item[2])
        self.ids.update_item_cost.text = str(item[3])
        self.ids.update_image.source = item[4]

    def CheckNumericStock(self, new_stock):
        itemm_stock = None
        if new_stock and new_stock.strip():
            try:
                itemm_stock = int(float(new_stock))
                if itemm_stock < 0:
                    WrongItemPopUp('Number of items should be postive.')
                    return None
            except:
                WrongItemPopUp('Stock number should be a number.')
                return None
        return itemm_stock

    def CheckNumericCost(self, new_cost):
        itemm_cost = None
        if new_cost and new_cost.strip():
            try:
                itemm_cost = float(new_cost)
                if itemm_cost < 0:
                    WrongItemPopUp('Item cost should be postive.')
                    return None
            except:
                WrongItemPopUp('Item cost should be number.')
                return None
        return itemm_cost

    def CheckItem_Update(self, new_stock, new_cost, new_name, new_image):
        item_id = self.ids.choose_item_id.text.strip()
        if len(item_id) > 1:
            item = self.db.get_item_properties(item_id)
            if item is None:
                WrongItemPopUp('Item id does not exist.')
                self.ResetDetails()
                return
        else:
            WrongItemPopUp('Empty item id.')
            self.ResetDetails()
            return
        new_name = None if len(new_name.strip())<1 else new_name.strip()
        new_image = None if len(new_image.strip())<1 else new_image.strip()
        new_item_details = [new_name, self.CheckNumericStock(new_stock), self.CheckNumericCost(new_cost), new_image, item[0]]
        if all(x is None for x in new_item_details[:-1]):
            WrongItemPopUp('Nothing to save.')
        else:
            for i, x in enumerate(new_item_details[:-1]):
                if x is None: 
                    new_item_details[i] = item[i+1]
                elif i == 1:
                    new_item_details[i] += item[2]

            # Updating database and main window widgets
            self.db.UpdateNewItemDetails(tuple(new_item_details))
            self.update_item_widget_main_store(new_item_details)
            WrongItemPopUp("Update sucessful.")
            self.RefreshScreen()
            self.ResetDetails()
            self.ids.choose_item_id.text = ''
        return

    def update_item_widget_main_store(self, new_item):
        get_all_items_screen_grid = self.sm.get_screen('all_items').ids.items_grid_layout
        need_update_ids = get_all_items_screen_grid.ids[new_item[-1]+'MainStore'].ids
        need_update_ids.item_name.text = new_item[0]
        need_update_ids.item_number.text = str(new_item[1])
        need_update_ids.item_cost.text = str(new_item[2])
        need_update_ids.image.source = new_item[3] 

    def ReturnBack(self):
        self.ResetDetails()
        self.ids.choose_item_id.text = ''
        self.RefreshScreen()
        self.sm.current = 'all_items'

    def ResetDetails(self):
        self.ids.update_item_name.text = ''
        self.ids.update_item_number.text = ''
        self.ids.update_item_cost.text = ''
        self.ids.update_image.source = ''

    def RefreshScreen(self):
        self.ids.update_item_name_new.text = ''
        self.ids.image_path.text = ' '
        self.ids.update_item_number_new.text = ''
        self.ids.update_item_cost_new.text = ''
        self.ids.camera_take_picture.disabled = False
        self.ids.new_image_path_here.source = ''
        self.ids.compare_old_image.source = ''

    def CameraClick(self):
        if NoCamera:
            WrongItemPopUp('Need camera permission. Enable camera permission from phone settings for this app.')
            self.ids.camera_take_picture.disabled = True
        else:
            self.sm.get_screen('take_picture').which_window = 'details_update'
            self.sm.current = 'take_picture'

    def delete_item_widget_main_store(self, item_id):
        get_all_items_screen_grid = self.sm.get_screen('all_items').ids.items_grid_layout
        get_all_items_screen_grid.remove_widget(get_all_items_screen_grid.ids[item_id+'MainStore'])

    def DeleteThings(self, item_id, item_name):
        self.db.DeleteItem(item_id)
        self.delete_item_widget_main_store(item_id)
        self.ids.choose_item_id.choiceslist.remove((item_id, item_id))
        self.ids.choose_item_id.choiceslist.remove((item_name, item_id))
        self.ResetDetails()
        self.ids.choose_item_id.text = ''
        WrongItemPopUp("Delete sucessful.")

    def PopupCallBackDeleteItemWindow(self, item_id, item_name, instance):
        self.DeleteThings(item_id, item_name)

    def PopUpDeleteItemWindow(self, popup_text, item_id, item_name):
        content = SetCustomerPopupBox()  
        pop = Popup(title=popup_text,
                      content=content,
                      size_hint=(0.5,0.5),
                      auto_dismiss = False)
        content.ids.CustomerPopupBox_btn1.bind(on_press=partial(self.PopupCallBackDeleteItemWindow, item_id, item_name))
        content.ids.CustomerPopupBox_btn1.bind(on_release=pop.dismiss)
        content.ids.CustomerPopupBox_btn2.bind(on_release= pop.dismiss)
        pop.open()
        return

    def DeleteFullItem(self):
        item_id = self.ids.choose_item_id.text.strip()
        if len(item_id) > 1:
            item = self.db.get_item_properties(item_id)
            if item is None:
                WrongItemPopUp('Item id does not exist.')
                self.ResetDetails()
                return
        else:
            WrongItemPopUp('Empty item id.')
            self.ResetDetails()
            return
        if item[4] != 'imgs/test.jpg':
            try:
                os.remove(item[4])
            except:
                self.PopUpDeleteItemWindow("Can't delete image. Do you want to force delete?", item_id, item[1])
                return
        self.DeleteThings(item_id, item[1])
        return

class CustomerCheckout(Screen):
    def __init__(self, db, sm, **kwargs):
        super(CustomerCheckout, self).__init__(**kwargs)
        self.ItemSummaryList = {}
        self.TrackItemCountList = {}
        self.DoClean = True
        self.sm = sm
        self.db = db
        self.ids.heading.add_widget(Heading(self.sm))

    def HelpPage(self):
        self.sm.get_screen('help_page').ids.help_page.goto('additem')
        self.DoClean = False
        self.sm.current = 'help_page'
    
    def InitializeScreen(self):
        if 'choose_item_id' not in self.ids:
            chooser = Chooser(self.sm,choiceslist=self.db.id_list(), hint_text='enter item name/id', size_hint=(0.5,None), pos_hint={'center_x':0.5, 'center_y':0.5})
            self.ids.choose_item_id_.add_widget(chooser)
            self.ids['choose_item_id'] = chooser
        else:
            self.ids.choose_item_id.choiceslist = self.db.id_list()
            if self.DoClean:
                self.ItemSummaryList.clear()
                self.TrackItemCountList.clear()

    def ShowItemDetails(self):
        item = self.db.get_item_properties(self.ids.choose_item_id.text.strip())
        self.ids.checkout_item_name.text = item[1]
        self.ids.checkout_item_cost.text = str(item[3])
        self.ids.checkout_image.source = item[4]
        temp_item_count = item[2]
        if item[0] in self.TrackItemCountList:
            temp_item_count = self.TrackItemCountList[item[0]]
        self.ids.checkout_item_number.text = str(temp_item_count)

    def ValidateEnteredItemNumber(self, new_item_numbers):
        try:
            new_item_numbers = int(new_item_numbers) if new_item_numbers is not None and len(new_item_numbers.strip())>0 else 0
        except:
            WrongItemPopUp("Count can't be fraction.")
            return 0
        if new_item_numbers == 0:
            WrongItemPopUp("No item to add.")
        
        return new_item_numbers

    def ValidateInputDiscount(self, discount_percent):
        discount_percent = discount_percent 
        if (discount_percent is not None) and (discount_percent.strip()): 
            try:
                discount_percent = float(discount_percent)
                if discount_percent < 0:
                    WrongItemPopUp('Price and discount should be postive.')
                    return None
            except:
                WrongItemPopUp("Price and discount should be number.")
                return None
        else:
            discount_percent = 0
        return discount_percent

    def CalculateFinalCost(self, item_current_cost, discount_percent):
        discount_amount = item_current_cost * discount_percent / 100
        final_cost_per_item = item_current_cost - discount_amount
        return final_cost_per_item

    def AddClicked(self):
        item_id = self.ids.choose_item_id.text.strip()
        if len(item_id) > 1:
            item = self.db.get_item_properties(item_id)
            if item is None:
                WrongItemPopUp('Item id does not exist.')
                self.ResetDetails()
                return
        else:
            WrongItemPopUp('Empty item id.')
            self.ResetDetails()
            return
        checkout_item_count = self.ValidateEnteredItemNumber(self.ids.Checkout_count.text)
        if checkout_item_count == 0: return 0
        tmp_item_cnt = int(self.ids.checkout_item_number.text)
        if int(item[2]) == 0:
            if checkout_item_count < 0:
                WrongItemPopUp("Trying to add extra item in original stock. Not allowed.")
            else:
                WrongItemPopUp("Item stock already empty.")
            #self.RefreshScreen()
            return 0
        elif (tmp_item_cnt - checkout_item_count < 0):
            if tmp_item_cnt == 0:
                WrongItemPopUp("No more item of this catagory in stock. All are sold.")
            else:
                WrongItemPopUp("Not enough items in stock.")
            #self.RefreshScreen()
            return 0
        elif (checkout_item_count < 0) and ((abs(checkout_item_count) + tmp_item_cnt) > int(item[2])):
            WrongItemPopUp("Trying to add extra item in original stock. Not allowed.")
            return 0
        else:
            discount_percent = self.ValidateInputDiscount(self.ids.Checkout_discount.text )
            if discount_percent is not None:
                final_cost = checkout_item_count * self.CalculateFinalCost(item[3], discount_percent)
                for_later = (item[0], item[1], checkout_item_count, item[3], discount_percent, final_cost)
                while True:
                    KEY = item[0] + '_' + RandomId(max_limit=10) + 'ItemsAdded'
                    if KEY not in self.ItemSummaryList: break
                self.ItemSummaryList[KEY] = for_later
                self.TrackItemCountList[item[0]] =  tmp_item_cnt - checkout_item_count 
            else:
                return 0
        self.AddItemWidget(KEY)
        self.RefreshScreen()

        return 1

    def UpdateLists(self, myid): # This function is for AddItemWidgetLabelV2
        update_count = self.ItemSummaryList[myid]
        if update_count[0] in self.TrackItemCountList:
            self.TrackItemCountList[update_count[0]] +=  update_count[2]

    def AddClickedPopup(self, item_name, item_count, item_price, item_discount):
        item_name = item_name.strip() if (item_name and len(item_name.strip()) > 0) else 'Unknown'
        checkout_item_count = self.ValidateEnteredItemNumber(item_count)
        if checkout_item_count == 0: return 0
        item_price = self.ValidateInputDiscount(item_price)
        item_discount = self.ValidateInputDiscount(item_discount)
        if (item_price is not None) and (item_discount is not None):
            final_cost = checkout_item_count * self.CalculateFinalCost(item_price, item_discount)
            for_later = ('unknown', item_name, checkout_item_count, item_price, item_discount, final_cost)
            while True:
                KEY = RandomId(max_limit=10) + 'ItemsAdded'
                if KEY not in self.ItemSummaryList: break
            self.ItemSummaryList[KEY] = for_later
        else:
            return 0
        self.AddItemWidget(KEY)

        return 1
    
    def PopupCallBack(self, pop, instance):
        name =  pop.content.ids.ExtraItemCheckout_item_name.text
        count = pop.content.ids.ExtraItemCheckout_item_count.text
        price = pop.content.ids.ExtraItemCheckout_item_price.text
        discount = pop.content.ids.ExtraItemCheckout_item_discount.text
        if self.AddClickedPopup(name, count, price, discount): pop.dismiss()

    def AddClickedNonItemPopUp(self):
        content = SetExtraItemCheckoutPopupBox()  
        pop = Popup(title='Non listed item checkout',
                      content=content,
                      size_hint=(0.9,0.5),
                      auto_dismiss = False)
        content.ids.ExtraItemCheckoutPopupBox_btn1.bind(on_press=partial(self.PopupCallBack, pop))
        content.ids.ExtraItemCheckoutPopupBox_btn2.bind(on_release=pop.dismiss)
        content.ids.ExtraItemCheckoutPopupBox_btn3.bind(on_press=partial(self.CleanPopupScreen, content))
        pop.open()
        return

    def CleanPopupScreen(self, content, instance):
        content.ids.ExtraItemCheckout_item_name.text = ''
        content.ids.ExtraItemCheckout_item_count.text = ''
        content.ids.ExtraItemCheckout_item_price.text = ''
        content.ids.ExtraItemCheckout_item_discount.text = ''

    def CutTexts(self, txt, max_limit = 15):
        if len(txt) > max_limit: 
            txt  = txt[:max_limit+1] + '...'
        else:
            txt = txt + '  '*(max_limit+3-len(txt)) 
        return txt

    def AddItemWidget(self, KEY):
        # https://stackoverflow.com/a/61707198
        scroll_vp_height = self.ids.add_item_label.viewport_size[1]
        scroll_height = self.ids.add_item_label.height

        label = AddItemWidgetLabelV2(self.sm) 
        label.my_id = KEY
        item = self.ItemSummaryList[KEY]
        label.ids.add_item_widget_label.text = self.CutTexts(item[0], 12) + ':  ' + self.CutTexts(item[1], 12) + ' --> ' + self.CutTexts(str(item[2]), 6)
        self.ids.add_item_label_box.add_widget(label)
        
        if scroll_vp_height > scroll_height:
            scroll_fact = self.ids.add_item_label.scroll_y
            bottom = scroll_fact * (scroll_vp_height-scroll_height)
            Clock.schedule_once(partial(self.adjust_scroll, bottom+label.height))

    def adjust_scroll(self, bottom, dt):
        scroll_vp_height = self.ids.add_item_label.viewport_size[1]
        scroll_height = self.ids.add_item_label.height
        self.ids.add_item_label.scroll_y = bottom / (scroll_vp_height-scroll_height)

    def ResetDetails(self):
        self.ids.checkout_item_name.text = ''
        self.ids.checkout_item_number.text = ''
        self.ids.checkout_item_cost.text = ''
        self.ids.checkout_image.source = ''

    def RefreshScreen(self):
        self.ResetDetails()
        self.ids.choose_item_id.text = ''
        self.ids.Checkout_count.text = '1'
        self.ids.Checkout_discount.text = '0'

    def ReturnBack(self):
        self.RefreshScreen()
        self.ids.add_item_label_box.clear_widgets()
        self.DoClean = True
        self.sm.current = 'all_items'

    def Submit(self):
        if len(self.ItemSummaryList) > 0:
            self.sm.current = 'customer_info'
            self.sm.current_screen.ids.checkout_button.disabled = False
            self.sm.current_screen.ids.checkout_back_button.disabled = False
            self.RefreshScreen()
        else:
            WrongItemPopUp('Click on "Add to bucket" and then "Checkout".')
        return

class SetExtraItemCheckoutPopupBox(BoxLayout):
    pass

class CustomerInfoScreen(Screen):
    def __init__(self, db, customer_db, sm, **kwargs):
        super(CustomerInfoScreen, self).__init__(**kwargs)
        self.sm = sm
        self.db = db
        self.customer_db = customer_db
        self.ids.heading.add_widget(Heading(self.sm))

    def HelpPage(self):
        self.sm.get_screen('help_page').ids.help_page.goto('additem')
        self.sm.current = 'help_page'

    def InitializeScreen(self):
        if 'choose_customer_id' not in self.ids:
            chooser = Chooser(self.sm,choiceslist=self.customer_db.id_list(), hint_text='customer name/id', pos_hint={'center_x':0.5, 'center_y':0.5})
            self.ids.customer_id.add_widget(chooser)
            self.ids['choose_customer_id'] = chooser
        else:
            self.ids.choose_customer_id.choiceslist = self.customer_db.id_list()

    def GenerateRandomId(self):
        self.ids.choose_customer_id.text = RandomId(max_limit=20, min_limit=10)

    def CheckLength_id(self, max_length=10):
        if len(self.ids.customer_id.text.strip()) > max_length:
            WrongItemPopUp(f'Maximum {max_length} character allowed.')
            self.ids.choose_customer_id.do_undo()

    def CheckLength_name(self, max_length=30):
        if len(self.ids.customer_name.text.strip()) > max_length:
            WrongItemPopUp(f'Maximum {max_length} character allowed.')
            self.ids.customer_name.do_undo()

    def CheckLength_contact(self, max_length=50):
        if len(self.ids.customer_contact.text.strip()) > max_length:
            WrongItemPopUp(f'Maximum {max_length} character allowed.')
            self.ids.customer_contact.do_undo()

    def CheckLength_comment(self, max_length=50):
        if len(self.ids.customer_comment.text.strip()) > max_length:
            WrongItemPopUp(f'Maximum {max_length} character allowed.')
            self.ids.customer_comment.do_undo()

    def CheckCustomer(self):
        self.customer_id_ = self.ids.choose_customer_id.text.strip()
        self.customer_name_ = self.ids.customer_name.text.strip()
        self.customer_contact_ = self.ids.customer_contact.text.strip()
        self.customer_comment_ = self.ids.customer_comment.text.strip()

        if (self.customer_id_ is None) or len(self.customer_id_) == 0:
            self.customer_id_ = RandomId(max_limit=20, min_limit=10)

        check_me = self.customer_db.check_customer_exists(self.customer_id_)
        if check_me:
            WrongItemPopUp('Customer id already exists. Provide new id.')
            return False
        else:
            if (self.customer_name_ is None) or len(self.customer_name_) == 0:
                WrongItemPopUp('Provide customer name.')
                return False
            #self.CleanFields()

        return True

    def Submit(self):
        if self.CheckCustomer():
            self.customer_db.add_new_customer([self.customer_id_, self.customer_name_, self.customer_contact_,0, self.customer_comment_])
            self.ids.choose_customer_id.choiceslist = self.customer_db.id_list()
            self.CleanFields()

    def UpdateCustomer(self):
        customer_id = self.ids.choose_customer_id.text
        if self.customer_db.check_customer_exists(customer_id) :
            update_customer_db = False
            customer_details_from_db = self.customer_db.get_customer_properties(customer_id)

            customer_name_ = self.ids.customer_name.text.strip()
            if customer_name_ and customer_name_!=customer_details_from_db[1]: # and len(customer_name_) > 0 : 
                update_customer_db = True
            else:
                customer_name_ = customer_details_from_db[1]

            customer_contact_ = self.ids.customer_contact.text.strip()
            if customer_contact_ and customer_contact_ != customer_details_from_db[2]: # and len(customer_contact_) > 0 : 
                update_customer_db = True
            else:
                customer_contact_ = customer_details_from_db[2]

            customer_comment_ = self.ids.customer_comment.text.strip()
            if customer_comment_ and customer_comment_ != customer_details_from_db[4]:# and len(customer_comment_) > 0 : 
                update_customer_db = True
            else:
                customer_comment_ = customer_details_from_db[4]

            if update_customer_db:
                self.customer_db.update_customer_details([customer_name_, customer_contact_, customer_comment_, customer_id])
                WrongItemPopUp('Update successful.')
                self.CleanFields()
            else:
                WrongItemPopUp('Nothing to update.')
        else:
            WrongItemPopUp('No data exists.')
            #self.CleanFields()
        return

    def DeleteCustomer(self):
        customer_id = self.ids.choose_customer_id.text
        if self.customer_db.check_customer_exists(customer_id) :
            self.customer_db.DeleteCustomer(customer_id)
            self.ids.choose_customer_id.choiceslist = self.customer_db.id_list()
            WrongItemPopUp('Delete successful.')
            self.CleanFields()
        else:
            WrongItemPopUp('No data exists.')

    def get_customer(self):
        customer_id = self.ids.choose_customer_id.text
        if self.customer_db.check_customer_exists(customer_id) :
            customer_details_from_db = self.customer_db.get_customer_properties(customer_id)
            self.ids.customer_name.text = customer_details_from_db[1]
            self.ids.customer_contact.text = customer_details_from_db[2]
            self.ids.customer_comment.text = customer_details_from_db[4]
        else:
            WrongItemPopUp('No data exists.')
            self.CleanFields()

    def ShowItemDetails(self):
        self.get_customer()

    def CleanFields(self):
        self.ids.choose_customer_id.text = ''
        self.ids.customer_name.text = ''
        self.ids.customer_contact.text = ''
        self.ids.customer_comment.text = ''

    def PopupCallBack(self, customer_name, customer_contact, instance):
        self.sm.get_screen('customer_checkout').ItemSummaryList['customer']=[customer_name, customer_contact]
        self.FinalizeCheckout()

    def PopUp(self, popup_text, customer_name, customer_contact):
        content = SetCustomerPopupBox()  
        pop = Popup(title=popup_text,
                      content=content,
                      size_hint=(0.5,0.5),
                      auto_dismiss = False)
        content.ids.CustomerPopupBox_btn1.bind(on_press=partial(self.PopupCallBack, customer_name, customer_contact))
        content.ids.CustomerPopupBox_btn1.bind(on_release=pop.dismiss)
        content.ids.CustomerPopupBox_btn2.bind(on_release=pop.dismiss)

        pop.open()

        return
        
    def CheckOut(self, **kwargs):
        customer_id = self.ids.choose_customer_id.text.strip()
        customer_namee = self.ids.customer_name.text.strip()
        customer_cont = self.ids.customer_contact.text.strip()
        if (customer_id is not None) and len(customer_id)>0:
            check_me = self.customer_db.check_customer_exists(customer_id)
            if check_me:
                self.customer_db.update_visit_count(customer_id)
            else:
                popup_text = 'No data exists under this customer id. Do you want to continue without customer info?'
                self.PopUp(popup_text,'','')
                return
        else:
            if ((customer_namee is not None) and len(customer_namee)>0) or ((customer_cont is not None) and len(customer_cont)>0):
                popup_text = 'Continuing with the one time customer info provided.'
                self.PopUp(popup_text,customer_namee,customer_cont)
                return
            else:
                popup_text = 'Continuing without customer info.'
                self.PopUp(popup_text,'','')
                return

        #print(sm.get_screen('customer_checkout').ItemSummaryList)
        self.sm.get_screen('customer_checkout').ItemSummaryList['customer']=[customer_namee, customer_cont]
        self.FinalizeCheckout()
        return True

    def ReturnBack(self):
        self.ids.checkout_button.disabled = False
        self.ids.checkout_back_button.disabled = False
        self.Quit()

    def Quit(self):
        self.CleanFields()
        self.sm.get_screen('customer_checkout').ids.add_item_label_box.clear_widgets()
        self.sm.get_screen('customer_checkout').DoClean = True
        self.sm.current = 'all_items'

    def BackToCheckoutItem(self):
        self.CleanFields()
        self.sm.get_screen('customer_checkout').DoClean = False
        self.sm.current = 'customer_checkout'

    def PrintConfirmationPopUp(self, popup_text, pdf, customer_name):
        content = SetCustomerPopupBox()  
        pop = Popup(title=popup_text,
                      content=content,
                      size_hint=(0.5,0.5),
                      auto_dismiss = False)
        content.ids.CustomerPopupBox_btn1.bind(on_press=partial(self.PrintPopupCallBack, pdf, customer_name))
        content.ids.CustomerPopupBox_btn1.bind(on_release=pop.dismiss)
        content.ids.CustomerPopupBox_btn2.bind(on_release=pop.dismiss)

        pop.open()

        return

    def PrintPopupCallBack(self, pdf, customer_name, instance):
        filepath_pdf = os.path.join(App.get_running_app().save_documents_dir, customer_name.replace(" ", "")+'_'+time.strftime("%Y%m%d_%H%M%S")+'.pdf')
        pdf.output(filepath_pdf)
        WrongItemPopUp(f"Chechout slip: {filepath_pdf}")

    def FinalizeCheckout(self):
        pdf, customer_name = self.PrintReport()
        self.PrintConfirmationPopUp('Do you want to print the checkout slip?', pdf, customer_name)
        self.UpdateDataBase_for_Item() # This needs to be after PrintReport()
        self.Quit()

    def PrintReport(self):
        self.summary_items = self.sm.get_screen('customer_checkout').ItemSummaryList
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt='******** Welcome to Inventory Manager ********', ln=1, align='C')

        Header_items = ['ID', 'NAME', 'COUNT', 'PRICE', 'DISCOUNT(%)', 'FINAL COST']
        col_width = pdf.w / (float(len(Header_items)) + 0.5)
        spacing = 1.5
        row_height = pdf.font_size * spacing

        customer_name = self.summary_items['customer'][0]
        customer_contact = self.summary_items['customer'][1]

        pdf.cell(0, 10, txt='-------- Checkout slip ---------', ln=1, align='C')
        pdf.cell(0, 10, txt=time.strftime("%d-%m-%Y  %H:%M:%S"), ln=1, align='R')
        pdf.ln(row_height)
        pdf.cell(0, 10, txt='Customer name: ' + customer_name, ln=1)
        pdf.cell(0, 10, txt='Customer contact: ' + customer_contact, ln=1)
        self.summary_items.pop('customer')
        pdf.ln(row_height)

        pdf.cell(0, 10, txt='='*80, ln=1, align='C')
        for hdr_fld in Header_items:
            pdf.cell(col_width, row_height, txt=str(hdr_fld), border=0)
        pdf.ln(row_height)
        pdf.cell(0, 10, txt='='*80, ln=1, align='C')
        pdf.ln(row_height)
        
        total_items = 0; total_cost = 0
        for item in self.summary_items:
            KK = self.summary_items[item]
            for col in KK:
                tmp_txt = str(col) 
                if len(tmp_txt)>8: tmp_txt = tmp_txt[:9] + '...'
                pdf.cell(col_width, row_height, txt=tmp_txt, border=0)
            total_items += KK[2]
            total_cost += KK[5]
            pdf.ln(row_height)

        pdf.cell(0, 10, txt='-'*150, ln=1, align='C')
        pdf.ln(row_height)
        pdf.cell(0, 10, txt='Total:' + ' '*50 + str(total_items) + ' '*80 + str(total_cost), ln=1)

        return pdf, customer_name


    def UpdateDataBase_for_Item(self):
        get_all_items_screen_grid = self.sm.get_screen('all_items').ids.items_grid_layout
        StockUpdate = []
        for item_id in self.summary_items:
            item = self.summary_items[item_id]
            StockUpdate.append((item[2],item[0]))
            if not item[0].startswith('unknown'):
                need_update_ids = get_all_items_screen_grid.ids[item[0]+'MainStore'].ids
                need_update_ids.item_number.text = str(int(need_update_ids.item_number.text) - int(item[2]))
        self.db.UpdateCheckoutItemStock(StockUpdate)

class SetCustomerPopupBox(BoxLayout):
    pass

class InventoryManagerApp(App):
    def __init__(self, **kwargs):
        super(InventoryManagerApp, self).__init__(**kwargs)
        self.previous_screen = "" 

    @property
    def image_storage_path(self):
        return self.save_image_dir

    def build(self):
        self.save_image_dir = self.config.get("General", 'image_save_path')
        self.save_documents_dir = self.config.get("General", 'document_save_path')
        self.DataBaseFile = self.config.get("General","database_save_path")
        self.DataBaseFile = os.path.join(self.DataBaseFile,'InventoryManagerDataBase.db')
        self.db = DataBase(self.DataBaseFile)
        self.customer_db = CustomerDataBase(self.DataBaseFile)
        self.sm = ScreenManager()
        
        screens = [ 
                    MainStoreWindow(self.db,self.sm, name="all_items"), 
                    AddItemWindow(self.db,self.sm,name='new_item_add'), 
                    UpdateItemDetails(self.db,self.sm,name='details_update'), 
                    CustomerInfoScreen(self.db, self.customer_db,self.sm,name='customer_info'), 
                    CustomerCheckout(self.db,self.sm,name='customer_checkout'), 
                    TakePicture(self.sm,name='take_picture'),
                    HelpPageScreen(self.sm,name='help_page')
                    ]
        
        for screen in screens:
            self.sm.add_widget(screen)

        self.use_kivy_settings = False

        Window.bind(on_keyboard=self.android_back_button)

        return self.sm

    def android_back_button(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            #if self.sm.current=='all_items': 
            #    self.stop()
            return True
        else:
            return False


    def build_config(self, config):
        default_path = self.user_data_dir
        config.setdefaults("General", {
                                        "image_save_path": default_path, 
                                        "database_save_path": default_path,
                                        "document_save_path": default_path})

    def build_settings(self, settings):
        #settings.add_json_panel("Settings", self.config, data=update_settings)
        settings.add_json_panel("Settings", self.config, data=update_settings_string_path)

    def WrongPathCallBack(self, pop, instance):
        self.close_settings()
        self.destroy_settings()
        self.open_settings()
        pop.dismiss()

    def WrongPath(self, pop_text):
        content = Button(text='Close',
                        size_hint_y=0.1) 
        pop = Popup(title=pop_text,
                      content=content,
                      size_hint=(0.5,0.5),
                      auto_dismiss = False)
        content.bind(on_press=partial(self.WrongPathCallBack, pop))
        pop.open()

    def on_config_change(self, config, section, key, value):
        if not os.path.isdir(value):
            config.set("General", key, self.user_data_dir)
            config.write()
            self.WrongPath("Path is not a directory or does not exists. Resetting to default path.")
        else:
            try:
                testfilepath = os.path.join(value, "testfile.txt")
                fp = open(testfilepath, 'w')
                fp.write(testfilepath)
                fp.close()
                os.remove(testfilepath)
            except:
                config.set("General", key, self.user_data_dir)
                config.write()
                self.WrongPath("Write permission denied. Resetting to default path.")
            else:
                if key == "image_save_path":
                    self.save_image_dir = value
                elif key == "database_save_path":
                    self.DataBaseFile = value
                elif key == 'document_save_path':
                    self.save_documents_dir = value


    def on_start(self, **kwargs):
        self.items = self.db.ReturnAllItems()
        if self.items:
            self.sm.get_screen('all_items').items = self.items
            del self.items
            gc.collect()
            self.sm.get_screen('all_items').ShowItemTemplates()
        else:
            self.sm.get_screen('all_items').AllItemGridLayout()

if __name__ == '__main__':
    __version__ = '0.1'
    InventoryManagerApp().run()
