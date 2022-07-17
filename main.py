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
from functools import partial
from kivy.clock import Clock
##from kivy.resources import resource_add_path, resource_find
from database import DataBase 
import string
import random
import os
import time
import gc
#from pdfrw import PdfWriter
from fpdf import FPDF

Builder.load_file('kvFiles/main_store_window.kv')
Builder.load_file('kvFiles/each_item_box_template.kv')

Builder.load_file('kvFiles/adding_new_item_window.kv')

Builder.load_file('kvFiles/updating_item_details_window.kv')
Builder.load_file('kvFiles/item_details_update_template.kv')
Builder.load_file('kvFiles/delete_item_template.kv')

Builder.load_file('kvFiles/customer_checkout.kv')
Builder.load_file('kvFiles/customer_checkout_popup_box.kv')

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
    def ValidateEnteredItemNumber(self, new_item_numbers):
        try:
            new_item_numbers = int(new_item_numbers) if new_item_numbers is not None and new_item_numbers.strip() else 0
        except:
            WrongItemPopUp("Count can't be fraction.")
            return 0
        if new_item_numbers < 0: WrongItemPopUp("Only positive number is allowed.")

        return new_item_numbers

    def CheckNegativeCount(self):
        if self.CheckCountNegative:
            WrongItemPopUp("Item stock already empty.")
        else:
            db.update_item_count(self.ids.item_id.text, self.updated_item_numbers)
            self.ids.item_number.text = str(self.updated_item_numbers)
        return 1

    def buttonAddClicked(self, item_id, new_item_numbers):
        new_item_numbers = self.ValidateEnteredItemNumber(new_item_numbers)
        if new_item_numbers > 0:
            self.updated_item_numbers, self.CheckCountNegative = db.validate_item_count(item_id, new_item_numbers, action='Add')
            self.CheckNegativeCount() 
            self.ids.NumberOfItemsAdd.text = '0'

    def buttonDeleteClicked(self, item_id, new_item_numbers):
        new_item_numbers = self.ValidateEnteredItemNumber(new_item_numbers)
        if new_item_numbers > 0:
            self.updated_item_numbers, self.CheckCountNegative = db.validate_item_count(item_id, new_item_numbers, action='Delete')
            self.CheckNegativeCount()
            self.ids.NumberOfItemsDelete.text = '0'
        

class MainStoreWindow(Screen):
    
    def ShowItemTemplates(self):
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        self.ids['items_grid_layout'] = layout
        for item in self.items:
            InstantItemBoxTemplate = ItemBoxTemplate()
            layout.ids[item[0]+'MainStore'] = InstantItemBoxTemplate
            InstantItemBoxTemplate.ids.item_id.text = item[0]
            InstantItemBoxTemplate.ids.item_name.text = item[1]
            InstantItemBoxTemplate.ids.item_number.text = str(item[2])
            InstantItemBoxTemplate.ids.item_cost.text = str(item[3])
            InstantItemBoxTemplate.ids.image.source = item[4]
            layout.add_widget(InstantItemBoxTemplate)
        self.ids.item_scroll.add_widget(layout)

    def AddItemBtn(self):
        sm.current = 'new_item_add'

    def DetailsUpdateScreen(self):
        sm.get_screen('details_update') .ids.update_item_window_.text = 'Update item details'
        sm.current = 'details_update'

    def DeleteItemScreen(self):
        sm.get_screen('delete_item').ids.update_item_window_.text = 'Delete item'
        sm.current = 'delete_item'

    def PrintSummary(self):
        self.summary_items = db.ReturnAllItems()
        if self.summary_items:
            # Create a popup for orientation
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, txt='******** Welcome to Inventory Manager ********', ln=1, align='C')

            col_width = pdf.w / 5.5
            spacing = 1.5
            row_height = pdf.font_size * spacing

            pdf.cell(0, 10, txt='='*80, ln=1, align='C')
            for hdr_fld in ['ID', 'NAME', 'COUNT', 'COST', 'IMAGE']:
                pdf.cell(col_width, row_height, txt=str(hdr_fld), border=0)
            pdf.ln(row_height)
            pdf.cell(0, 10, txt='='*80, ln=1, align='C')
            pdf.ln(row_height)

            for item in self.summary_items:
                for col in item:
                    pdf.cell(col_width, row_height, txt=str(col), border=0)
                pdf.ln(row_height)
                #row_item = ''.join([str(col).strip().rjust(20) + " " for  col in item])
                #pdf.cell(0, 10, txt = row_item, ln=1, align='C')

            filepath_pdf = 'ItemsSummary_'+time.strftime("%Y%m%d_%H%M%S")+'.pdf'
            pdf.output(filepath_pdf)
            WrongItemPopUp(f"Items summary: {filepath_pdf}")
        else:
            WrongItemPopUp("No item exists.")

    def CustomerCheckOut(self):
        sm.current = 'customer_checkout'

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

    def ID_list(self):
        self.item_id_list_db = db.id_list()
        return 

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
            WrongItemPopUp(f'Maximum {max_length} character allowed.')
            self.ids.item_name.do_undo()

    def CheckLength_id(self, max_length = 6):
        if len(self.ids.item_id.text.strip()) > max_length:
            WrongItemPopUp(f'Maximum {max_length} character allowed.')
            self.ids.item_id.do_undo()

    def CheckItemsEligibility(self):
        item_id, item_name, item_numbers, item_cost, item_img_path = \
        self.item_id.text.strip(), self.item_namee.text.strip(), self.item_number.text.strip(),\
        self.item_cost.text.strip(), self.image.text.strip()

        #check_item_id_database = True if item_id in self.item_id_list_db else False
        check_item_id_database = db.check_item_eligibility(item_id)

        if not item_id:
            WrongItemPopUp('Item id is mandatory. Supply an appropriate unique item id.')
            return False
        if not item_name:
            WrongItemPopUp('Item name is mandatory. Supply an appropriate item name.')
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
            WrongItemPopUp('Only png and jpeg images are allowed.')
            return False

        if check_item_id_database or (item_id in self.ItemListIds):
            WrongItemPopUp('Item id already exists. Provide new id.')
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
            self.add_new_item_widget_main_store()
            self.ReturnBack()
        else:
            WrongItemPopUp('Click on "Add to bucket" and then "Save".')
        return 

    def add_new_item_widget_main_store(self):
        get_all_items_screen_grid = sm.get_screen('all_items').ids.items_grid_layout
        for item_i in self.ItemList:
            InstantItemBoxTemplate = ItemBoxTemplate()
            InstantItemBoxTemplate.ids.item_id.text = item_i[0]
            InstantItemBoxTemplate.ids.item_name.text = item_i[1]
            InstantItemBoxTemplate.ids.item_number.text = str(item_i[2])
            InstantItemBoxTemplate.ids.item_cost.text = str(item_i[3])
            InstantItemBoxTemplate.ids.image.source = item_i[4]
            get_all_items_screen_grid.add_widget(InstantItemBoxTemplate)
            get_all_items_screen_grid.ids[item_i[0]+'MainStore'] = InstantItemBoxTemplate

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

class AddItemWidgetLabelV2(BoxLayout):
    def CheckoutDeleteItemFromList(self, which_id_delete):
        my_screen = sm.get_screen('customer_checkout')
        imy_id = which_id_delete.split(':')[0].strip()
        my_screen.CheckoutSummaryList.pop(imy_id)
        imy_id += 'Checkout'
        my_screen.ids.add_item_label_box.remove_widget(my_screen.ids[imy_id])


class UpdateItemProperties(BoxLayout):
    def __init__(self, **kwargs):
        super(UpdateItemProperties, self).__init__(**kwargs)
        self.itemm = [None]*4
        self.save_and_back = False

    def CheckNumericCost(self, new_cost):
        if new_cost and new_cost.strip():
            try:
                self.itemm[3] = float(new_cost)
                if self.itemm[3] < 0:
                    WrongItemPopUp('Item cost should be postive.')
                    return 0
                self.save_and_back = True
            except:
                WrongItemPopUp('Item cost should be number.')
                #self.ids.update_item_cost_new.text = ''
                return 0
        return 1

    def UpdateDataBase_for_Item(self, new_name, new_image):
        if new_name and new_name.strip(): 
            self.itemm[1] = new_name.strip() 
            self.save_and_back = True

        if new_image and new_image.strip(): 
            self.itemm[4] = new_image.strip()
            self.save_and_back = True

        if self.save_and_back:
            db.UpdateNewItemDetails(tuple(map(self.itemm.__getitem__, [1, 3, 4, 0])))
            self.update_item_widget_main_store()
            WrongItemPopUp("Update sucessful.")
            self.RefreshScreen()
        else:
            WrongItemPopUp('Nothing to save.')

    def update_item_widget_main_store(self):
        get_all_items_screen_grid = sm.get_screen('all_items').ids.items_grid_layout
        need_update_ids = get_all_items_screen_grid.ids[self.itemm[0]+'MainStore'].ids
        need_update_ids.item_name.text = self.itemm[1]
        need_update_ids.item_cost.text = str(self.itemm[3])
        need_update_ids.image.source = self.itemm[4] 

    def RefreshScreen(self):
        sm.get_screen('details_update').ResetDetails()
        self.ids.update_item_name_new.text = ''
        self.ids.image_path.text = ''
        self.ids.update_item_cost_new.text = ''
        self.ids.camera_take_picture.disabled = False
        self.save_and_back = False

    def CameraClick(self):
        if NoCamera:
            WrongItemPopUp('Need camera permission. Enable camera permission from phone settings for this app.')
            self.ids.camera_take_picture.disabled = True
        else:
            sm.get_screen('take_picture').which_window = 'details_update'
            sm.current = 'take_picture'

    def ReturnBack(self):
        self.RefreshScreen()
        sm.current = 'all_items'

class DeleteItem(BoxLayout):
    def __init__(self, **kwargs):
        super(DeleteItem, self).__init__(**kwargs)
        self.itemm = None

    def DeleteItemDataBase(self):
        if self.itemm[4] != 'imgs/test.jpg' and self.itemm[4] != 'imgs/presplash.png':
            try:
                os.remove(self.itemm[4])
            except:
                WrongItemPopUp("Can't delete image.")
                return
        db.DeleteItem(self.itemm[0])

        WrongItemPopUp("Delete sucessful.")
        self.delete_item_widget_main_store()
        #sm.get_screen('delete_item').ids.choose_item_id.values.remove(self.itemm[0])
        sm.get_screen('delete_item').ids.choose_item_id.choiceslist.remove(self.itemm[0])
        self.RefreshScreen()
        return

    def delete_item_widget_main_store(self):
        get_all_items_screen_grid = sm.get_screen('all_items').ids.items_grid_layout
        get_all_items_screen_grid.remove_widget(get_all_items_screen_grid.ids[self.itemm[0]+'MainStore'])

    def RefreshScreen(self):
        sm.get_screen('delete_item').ResetDetails()

    def ReturnBack(self):
        self.RefreshScreen()
        sm.current = 'all_items'

# https://stackoverflow.com/a/59805349
class Chooser(TextInput):
    choiceslist = ListProperty([])

    def __init__(self, **kwargs):
        self.choiceslist = kwargs.pop('choiceslist', [])  # list of choices
        super(Chooser, self).__init__(**kwargs)
        self.multiline = False
        self.cursor_color = [0,0,0,1]
        self.size_hint = (0.9, 0.9)
        self.halign = 'left'
        self.bind(text=self.on_text)
        self.dropdown = None
        self.suggestion_text = None

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

    def on_text(self, chooser, text):
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None
        if text == '':
            return
        values = []
        for addr in self.choiceslist:
            if addr.startswith(text):
                values.append(addr)
        self.values = values
        if len(values) > 0:
            if len(self.text) < len(self.values[0]):
                self.suggestion_text = self.values[0][len(self.text):]
            else:
                self.suggestion_text = ' '  # setting suggestion_text to '' screws everything
            self.dropdown = DropDown()
            for val in self.values:
                self.dropdown.add_widget(Button(text=val, size_hint_y=None, height=48, on_release=self.do_choose))
            self.dropdown.open(self)

    def do_choose(self, butt):
        self.text = butt.text
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None


class UpdateItemDetails(Screen):
    action = StringProperty()

    def ID_list(self):
        self.ids.choose_item_id.values = db.id_list()
    
    def SpecificLayoutItemDetails_or_Delete(self, llayout):
        self.ids['item_details_specific_layout'] = llayout
        self.ids.update_item_id_row.add_widget(llayout)
        self.ids.item_details_specific_layout.disabled = True

    def InitializeScreen(self):
        #self.ID_list()
        if 'item_details_specific_layout' not in self.ids:
            if sm.current == 'details_update':
                self.SpecificLayoutItemDetails_or_Delete(UpdateItemProperties())
            elif sm.current == 'delete_item':
                self.SpecificLayoutItemDetails_or_Delete(DeleteItem())
            else:
                pass
            chooser = Chooser(choiceslist=db.id_list(), hint_text='Enter ID', size_hint=(0.5,None), height=30, pos_hint={'center_x':0.5, 'center_y':0.5})
            self.ids.choose_item_id_.add_widget(chooser)
            self.ids['choose_item_id'] = chooser
        else:
            self.ids.choose_item_id.choiceslist = db.id_list()

    def get_item_details(self):
        self.item_id = self.ids.choose_item_id.text 
        if self.item_id and self.item_id.strip():
            self.item = db.get_item_properties(self.item_id.strip())
            if self.item is None: 
                WrongItemPopUp('Item id does not exist.')
                return 0
        else:
            WrongItemPopUp('Please supply the item id.')
            return 0
        self.ids.choose_item_id_box_id.disabled = True
        self.ids.choose_item_id_box_id_.disabled = True
        self.ids.item_details_specific_layout.disabled = False
        return 1

    def ShowItemDetails(self):
        self.ids.update_item_id.text = self.item[0]
        self.ids.update_item_name.text = self.item[1]
        self.ids.update_item_number.text = str(self.item[2])
        self.ids.update_item_cost.text = str(self.item[3])
        self.ids.update_image.source = self.item[4]
        self.PassItemDetails_to_other_children()

    def PassItemDetails_to_other_children(self):
        self.ids.item_details_specific_layout.itemm = list(self.item)
    
    def ReturnBack(self):
        self.ResetDetails()
        sm.current = 'all_items'

    def ResetDetails_part(self):
        self.ids.update_item_id.text = ''
        self.ids.update_item_name.text = ''
        self.ids.update_item_number.text = ''
        self.ids.update_item_cost.text = ''
        self.ids.update_image.source = ''
        self.ids.choose_item_id.text = ''

    def ResetDetails(self):
        self.ResetDetails_part()
        self.ids.choose_item_id_box_id.disabled = False
        self.ids.choose_item_id_box_id_.disabled = False
        self.ids.item_details_specific_layout.disabled = True

class CustomerCheckout(Screen):
    def __init__(self, **kwargs):
        super(CustomerCheckout, self).__init__(**kwargs)
        self.CheckoutSummaryList = {}

    def ID_list(self):
        self.ids.choose_item_id.values = db.id_list()
    
    def InitializeScreen(self):
        #self.ID_list()
        if 'choose_item_id' not in self.ids:
            chooser = Chooser(choiceslist=db.id_list(), hint_text='Enter ID', size_hint=(0.5,None), height=30, pos_hint={'center_x':0.5, 'center_y':0.5})
            self.ids.choose_item_id_.add_widget(chooser)
            self.ids['choose_item_id'] = chooser
        else:
            self.ids.choose_item_id.choiceslist = db.id_list()
        self.ids.update_box_template.disabled = True
        self.ids.final_checkout_box_add.disabled = True
        self.CheckoutSummaryList.clear()

    def get_item_details(self):
        self.item_id = self.ids.choose_item_id.text 
        if self.item_id and self.item_id.strip():
            self.item = db.get_item_properties(self.item_id.strip())
            if self.item is None: 
                WrongItemPopUp('Item id does not exist.')
                return 0
        else:
            WrongItemPopUp('Please supply the item id.')
            return 0
        self.ids.choose_item_id_box_id.disabled = True
        self.ids.choose_item_id_box_id_.disabled = True
        self.ids.update_box_template.disabled = False
        self.ids.final_checkout_box_add.disabled = False
        return 1

    def ShowItemDetails(self):
        self.ids.checkout_item_name.text = self.item[1]
        self.ids.checkout_item_cost.text = str(self.item[3])
        self.ids.checkout_image.source = self.item[4]
        temp_item_count = self.item[2]
        if self.item[0] in self.CheckoutSummaryList:
            temp_item_count -= sum([full_item[2] for full_item in self.CheckoutSummaryList[self.item[0]]])
        self.ids.checkout_item_number.text = str(temp_item_count)

    def ValidateEnteredItemNumber(self):
        new_item_numbers = self.ids.Checkout_count.text 
        try:
            new_item_numbers = int(new_item_numbers) if new_item_numbers is not None and new_item_numbers.strip() else 0
        except:
            WrongItemPopUp("Count can't be fraction.")
            return 0
        if new_item_numbers < 0: 
            WrongItemPopUp("Only positive number is allowed.")
        elif new_item_numbers == 0:
            WrongItemPopUp("No item to add.")
        
        return new_item_numbers

    def ValidateInputDiscount(self):
        self.discount_percent = self.ids.Checkout_discount.text
        if self.discount_percent is not None and self.discount_percent.strip():
            try:
                self.discount_percent = float(self.discount_percent)
                if self.discount_percent < 0:
                    WrongItemPopUp('Item cost should be postive.')
                    return 0
            except:
                WrongItemPopUp("Only numbers are allowed.")
                return 0
        else:
            self.discount_percent = 0
        return 1

    def CalculateFinalCost(self):
        item_current_cost = self.item[3]
        discount_amount = item_current_cost * self.discount_percent / 100
        final_cost_per_item = item_current_cost - discount_amount
        return final_cost_per_item

    def AddClicked(self):
        self.checkout_item_count = self.ValidateEnteredItemNumber()
        if self.checkout_item_count > 0:
            self.updated_item_numbers, self.CheckCountNegative = db.validate_item_count(self.item[0], self.checkout_item_count, action='Delete')
            if self.CheckCountNegative:
                WrongItemPopUp("Item stock already empty.")
                self.RefreshScreen()
                return 0
            else:
                if self.ValidateInputDiscount():
                    self.final_cost = self.checkout_item_count * self.CalculateFinalCost()
                    for_later = (self.item[0], self.item[1], self.checkout_item_count, self.item[3], self.discount_percent, self.final_cost)
                    if self.item[0] in self.CheckoutSummaryList:
                        self.CheckoutSummaryList[self.item[0]].append(for_later)
                    else:
                        self.CheckoutSummaryList[self.item[0]] = [for_later]
                    self.ids.Checkout_count.text = '1'
                    self.ids.Checkout_discount.text = '0'
                else:
                    return 0
            self.AddItemWidget()
            self.RefreshScreen()
        else:
            pass

        return 1

    def AddItemWidget(self):
        # https://stackoverflow.com/a/61707198
        scroll_vp_height = self.ids.add_item_label.viewport_size[1]
        scroll_height = self.ids.add_item_label.height

        label = AddItemWidgetLabelV2() 
        
        label.ids.add_item_widget_label.text = ' '*6 + self.item[0] + ':  ' + self.item[1] + ' --> ' + str(self.checkout_item_count) + ', ' + str(self.final_cost)
        self.ids.add_item_label_box.add_widget(label)
        self.ids[self.item[0]+'Checkout'] = label
        
        if scroll_vp_height > scroll_height:
            scroll_fact = self.ids.add_item_label_box.scroll_y
            bottom = scroll_fact * (scroll_vp_height-scroll_height)
            Clock.schedule_once(partial(self.adjust_scroll, bottom+label.height))

    def adjust_scroll(self, bottom, dt):
        scroll_vp_height = self.ids.add_item_label_box.viewport_size[1]
        scroll_height = self.ids.add_item_label_box.height
        self.ids.add_item_label_box.scroll_y = bottom / (scroll_vp_height-scroll_height)

    def ResetDetails(self):
        self.ids.checkout_item_name.text = ''
        self.ids.checkout_item_number.text = ''
        self.ids.checkout_item_cost.text = ''
        self.ids.checkout_image.source = ''
        self.ids.choose_item_id.text = ''

    def ResetDisable(self):
        self.ids.choose_item_id_box_id.disabled = False
        self.ids.choose_item_id_box_id_.disabled = False
        self.ids.update_box_template.disabled = True
        self.ids.final_checkout_box_add.disabled = True

    def RefreshScreen(self):
        self.ResetDetails()
        self.ResetDisable()

    def ReturnBack(self):
        self.RefreshScreen()
        self.ids.Checkout_count.text = '1'
        self.ids.Checkout_discount.text = '0'
        self.ids.add_item_label_box.clear_widgets()
        sm.current = 'all_items'

    def Submit(self):
        if len(self.CheckoutSummaryList) > 0:
            print(self.CheckoutSummaryList)
            savedialog()
            #db.add_new_items(self.ItemList)
            #self.add_new_item_widget_main_store()

            #self.ReturnBack()
        else:
            WrongItemPopUp('Click on "Add to bucket" and then "Save".')
        return 

   #     sm.current = 'enter_customer'
   #     for row in self.NeedUpdateLater_Count:

   # def update_item_widget_main_store(self):
   #     get_all_items_screen_grid = sm.get_screen('all_items').ids.items_grid_layout
   #     need_update_ids = get_all_items_screen_grid.ids[self.item[0]+'MainStore'].ids
   #     need_update_ids.item_number.text = str(self.item[2])


   # def delete_item_widget_main_store(self):
   #     get_all_items_screen_grid = sm.get_screen('all_items').ids.items_grid_layout
   #     get_all_items_screen_grid.remove_widget(get_all_items_screen_grid.ids[self.itemm[0]+'MainStore'])


def WrongItemPopUp(popup_text):
    content = Button(text='Close',
                    size_hint_y=0.1) 
    pop = Popup(title=popup_text,
                  content=content,
                  size_hint=(0.5,0.5),
                  auto_dismiss = True)
    content.bind(on_press=pop.dismiss)

    pop.open()

class savedialog(BoxLayout):
    def __init__(self,**kwargs):
        super(savedialog,self).__init__(**kwargs)
        self.save_popup = SetCustomerPopup(self)

    def save(self, *args):
        self.save_popup.open()

class SetCustomerPopupBox(BoxLayout):
    pass
    
class SetCustomerPopup(Popup):
    def __init__(self, savedialog, **kwargs):
        super(SetCustomerPopup, self).__init__(**kwargs)

        self.content = SetCustomerPopupBox()

        self.savedialog = savedialog

    def save(self, **kwargs):
        _ = self.savedialog.name_input.text
        self.dismiss()

    def cancel(self,*args):
        self.dismiss()


class WindowManager(ScreenManager):
    pass

sm = WindowManager()

screens = [ MainStoreWindow(name="all_items"), 
            AddItemWindow(name='new_item_add'), 
            UpdateItemDetails(name='details_update'), \
            UpdateItemDetails(name='delete_item'), \
            CustomerCheckout(name='customer_checkout'), \
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

    def on_start(self, **kwargs):
        self.items = db.ReturnAllItems()
        if self.items:
            sm.get_screen('all_items').items = self.items
            del self.items
            gc.collect()
            sm.get_screen('all_items').ShowItemTemplates()

if __name__ == '__main__':
    __version__ = '0.1'
    InventoryManagerApp().run()
