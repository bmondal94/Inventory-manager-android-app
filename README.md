# Inventory-manager-android-app
This is an **android app** for managing your inventory items. The `apk` file is in the `bin/` folder. 

# The `apk` file
* ![Download](bin/inventorymanager-0.1-arm64-v8a_armeabi-v7a-debug.apk)

# Details
* The app was created with `python kivy` and builded using `Buildozer` .
* The app needs additional CAMERA permission to take picture of an item if needed. 
* It creates a `sqlite` database for the items: "InventoryManagerDataBase.db"
* Each item has
  * `Name`: a name
  * `ID`: an item id
  * `Stock`: total number of items in stock
  * `Price`: cost of the item
  * `Image`: an identification image of the item
 * You can change item stock easily. 
 * You can `Add` or `Delete` or `Update` item (details).
 * You can review the `Summary` of the all the items in your stock.
* You can apply the customer checkout.
 * `Information`: to add, delete or update the customer information.
 * `Checkout`: checkout the items.
 
# Button details

<img src='imgs/app/settings.png' height=50> : To change the default image path, database path and the path for documents(e.g. checkout slip) to be saved.

<img src='imgs/app/help.png' height=50> : To go the manual page. 

## Main store
* Here you can change item counts and `Add`, `Update`, or `Delete` an item.
  * **Search**: To search an item in the below list.
  * <img src='imgs/app/delete.jpg' height=30> : To delete an item in the store. You can use this icon to delete the item or ``Delete`` button from below.
  * **+** : To increase the item count. You can put the number of item you want to change in the text box next to the `+` icon. 
  And then click on `+` icon.
  * **-** : To deduct the item count. You can put the number of item you want to change in the text box next to the `-` icon. 
  And then click on `-` icon.
  * <img src='imgs/app/update.jpg' height=30> : To update an item details. You can use this icon to update the item or ``Update`` button from below.
  * **Add**: To add new item in the store.
  * **Update**: To update an item details, such as item cost. 
  * **Delete**: To delete an item.
  * **Summary** : To review the summary of all the items in your inventory.
  * **Information** : Add/update the customer information in the database.
  * **Checkout**: Customer checkout option.
  * **Quit**: To quit the app.
  
## Add new items
* Here you can add new item(s). 
  * **Name** : Name of the new item. This is mandatory.
  * **ID** : The unique id of the item. The id should be unique. This is mandatory. You can also generate random ID.
  * <img src='imgs/app/random2.jpg' height=30> : Generates random ID.
  * **Stock**: Total of item of this category in the inventory. Defauls is 0. If nothing is supplied 0 will be used.
  * **Price (/item)**: Item cost per item.  Defauls is 0. If nothing is supplied 0 will be used.
  * **Image**: The image for the item. You can add it manually. Write the image path in the ``Image`` text field. Default is 'imgs/test.jpg'. or,
  * <img src='imgs/app/folder.jpg' height=30> : Choose an image from your device. or,
  * <img src='imgs/app/camera.jpg' height=30> : Take a picture of the item.
  * **Add to bucket**: After you entry the item details you have to add it to the bucket. Then `Save` it. If you don't add the item to bucket the item can not be save. 
  You can add multiple items in the bucket. Each time you add a valid item, you will find it in the `Items added` list. 
  * **Save**: Finally save all your items in the bucket.
  * **Home**: Go back to the home page.
  * **Quit**: To quit the app.
   
**Tips:**

* Don't want to add an image to item properties. Add '0.png' in the image field. It will show blank image. 

**Note:**

* Camera can be used multiple times. Every time you take a picture it will be saved inside the image folder. Please manually delete unnecessary images to avaoid clutter and memory damage.App will not delete the unnecessary images because you may want to change your mind to use the previously taken image. Then you can use the `folder icon` to navigate and choose the image.
* If you use blank image during delete process you will get a warning that image could not found. You have to force delete the item. 

## Update item details
* Update the item details such as item name, image and cost.
  * **Item ID**: Please choose the item name or id from the list for which you want to update the details. 
  * **New name**: Put the new name in this text field.
  * **New stock**: Put the new stock in this text field. This will be added to old stock. 
  * **New price**: Put the new price in this text field.
  * **New image**: Put the new image in this text field. or,
  * <img src='imgs/app/folder.jpg' height=30> : Choose an image from your device. or,
  * <img src='imgs/app/camera.jpg' height=30> : Take a picture of the item.
  * **Save**: Finally, save the update.
  * **Refresh**: Reset the window for new input.
  * **Home**: Go back to the home page.
  * **Quit**: To quit the app.
   
**Tips:**

* Don't want to add an image to item properties. Add '0.png' in the image field. It will show blank image. 

**Note:**

* Camera can be used multiple times. Every time you take a picture it will be saved inside the image folder. Please manually delete unnecessary images to avaoid clutter and memory damage.App will not delete the unnecessary images because you may want to change your mind to use the previously taken image. Then you can use the `folder icon` to navigate and choose the image.
* If you use blank image during delete process you will get a warning that image could not found. You have to force delete the item.  
 
## Delete item
* To delete an item.
  * **Item ID**: Please choose the item name or id from the list for which you want to update the details. 
  * **Remove**: To delete the item click here.
  * **Home**: Go back to the home page.
  * **Quit**: To quit the app.

## Customer info
* For customer formation.
  * **ID**: Add or generate a random customer identification number. 
  * **Name**: Put the new name in this text field.
  * **Contact**: Put the customer contact in this text field.
  * **Comment**: Put the remarks in this text field. For e.g. previous debt etc. 
  * **Add**: To add new customer information in the database.
  * **Update**: To update the customer details.
  * **Delete**: To delete a customer information from the database.
  * **Refresh**: Reset the window for new input.
  * **Checkout**: To add (not mandatory) customer details in the checkout slip.
  * **Back**: Go back to the previous page for updating the checkout item list.
  * **Home**: Go back to the home page.
  * **Quit**: To quit the app.

## Customer checkout
* For customer checkout.
  * **Item ID**: Please choose the item name or id from the list for which you want to update the details. 
  * **Count**: How many items do you want to checkout? This can be negative.
  * **Discount**: The discount percent (per item) on the item cost. The default is 0 %.
  * **Add to bucket**: After you entry the item details you have to add it to the bucket. Then `Save` it. If you don't add the item to bucket the item can not be save. 
  You can add multiple items in the bucket. Each time you add a valid item, you will find it in the `Items added` list. 
  * **Add non-listed item**: To add an item which is not in the database. Or, to add previous debt etc.
  * **Checkout**: Finally save all your items in the bucket. And move to page to add customer information in the checkout.
  * **Refresh**: Reset the window for new input. **Warning**, this will delete all the previously added items from the checkout list.
  * **Home**: Go back to the home page.
  * **Quit**: To quit the app.
  
# Screens
###
<img src='ScreenShots/page1.jpg' height='500'>  <img src='ScreenShots/page2.jpg' height='500'>  <img src='ScreenShots/page3.jpg' height='500'>
<img src='ScreenShots/page4.jpg' height='500'>  <img src='ScreenShots/page5.jpg' height='500'>  <img src='ScreenShots/page6.jpg' height='500'>
<img src='ScreenShots/page7.jpg' height='500'>  <img src='ScreenShots/page8.jpg' height='500'>	<img src='ScreenShots/page9.jpg' height='500'>  
<img src='ScreenShots/page10.jpg' height='500'>  <img src='ScreenShots/page11.jpg' height='500'>  <img src='ScreenShots/page12.jpg' height='500'>


  
# LICENSE
  GNU General Public License (GPLv3). It is completely free and open source.
  
# Troubleshooting
1. **App crashes on start**
	* Please enable the `camera` access for this app in the phone settings.
	 
2. **Can't change settings. Showing 'write permission denied'.**
    * Please enable `Allow management of all files` for this app in the phone settings.
