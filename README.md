# Inventory-manager-android-app
This is an **android app** for managing your inventory items. The `apk` file is in the `bin/` folder. 

# The `apk` file
* ![Download](bin/inventorymanager-0.1-arm64-v8a_armeabi-v7a-debug.apk)

# Details
* The app was created with `python kivy` and build using `Buildozer` .
* The app needs additional CAMERA permission to take picture of an item if needed. 
* It creates a `sqlite` database for the items: "StoreData.db"
* Each item has
  * a name
  * `ID`: item id
  * `Count`: number of items
  * `Cost`: cost of an item
 * You can change item counts easily. 
 * You can `Add` or `Delete` or `Update` item (details).
 * You can `Print` the summary of the all the items in your stock.
* You can apply the customer check-out.
 * `Information`: To add ot delete or update the customer information.
 * `Check-out`: Customer check-out window. 
 
# Button details
## Main store
* Here you can change item counts and `Add`, `Update`, or `Delete` an item.
  * **+** : To increase the item count. You can put the number of item you want to change in the text box next to the `+` symbol. 
  And then click on `+` sign.
  * **-** : To deduct the item count. You can put the number of item you want to change in the text box next to the `-` symbol. 
  And then click on `-` sign.
  * **Add**: To add new item in the store.
  * **Update**: To update an item details, such as item cost.
  * **Delete**: To delete an item.
  * **Print** : To print the summary of all the items.
  * **Information** : Add/update the customer.
  * **Check-out**: Customer check-out option.
  
## Add new items
* Here you can add new item (s). 
  * **Item name** : Name of the new item. This is mandatory.
  * **Item ID** : The unique id of the item. The id should be unique. This is mandatory. You can also generate random ID.
  * **Generate**: Generates random ID.
  * **Item counts**: Number count of that item. Defauls is 0. If nothing is supplied 0 will be used.
  * **Item cost**: Item cost per item.  Defauls is 0. If nothing is supplied 0 will be used.
  * **Image**: The image for the item. You can add it manually or you can use the camera to `Take picutre`. Defaults 'imgs/test.jpg'.
  * **Camera**: To take a picture of the item.
  * **Add to bucket**: After you entry the item details you have to add it to the bucket. Then `Save` it. If you don't add the item to bucket the item can not be save. 
  You can add multiple items in the bucket. Each time you add a valid item, you will find it in the `Items added` list. 
  * **Save**: Finally save all your items in the bucket.
  * **Quit**: If you want to quit.
  
## Update item details
* Update the item details such as item name, image and cost.
  * **Item ID**: Please choose the `item ID` for which you want to update the details. 
  * **Show**: On click you will see the details about the item.
  * **Back**: If you want to go back.
  * **New name**: Put the new name in this text field.
  * **New image**: Put the new image in this text field. or,
  * **Camera**: Take a picture of the item.
  * **New cost**: Put the new cost in this text field.
  * **Save**: Finally save the update.
  * **Refresh**: Reset the window for new input.
  * **Quit**: If you want to quit.
  
  
## Delete item
* To delete an item.
  * **Item ID**: Please choose the `item ID` for which you want to update the details. 
  * **Show**: On click you will see the details about the item.
  * **Back**: If you want to go back.
  * **Confirm**: To delete the item click here.
  * **Refresh**: Reset the window for new input.
  * **Quit**: If you want to quit.

## Customer checkout
* For customer checkout.
  * **Item ID**: Please choose the `item ID` for which you want to update the details. 
  * **Show**: On click you will see the details about the item.
  * **Back**: If you want to go back.
  * **Count**: How many items do you want to check-out? 
  * **Discount**: The discount percent (per item) on the item cost. The default is 0 %.
  * **Add to bucket**: After you entry the item details you have to add it to the bucket. Then `Save` it. If you don't add the item to bucket the item can not be save. 
  You can add multiple items in the bucket. Each time you add a valid item, you will find it in the `Items added` list. 
  * **Save**: Finally save all your items in the bucket.
  * **Quit**: If you want to quit.
  
# Screens
###
<img src='ScreenShots/page1.jpg' height='500'>  <img src='ScreenShots/page2.jpg' height='500'>  <img src='ScreenShots/page3.jpg' height='500'>
<img src='ScreenShots/page4.jpg' height='500'>


  
# LICENSE
  GNU General Public License. It is completely free and open source.
  
# Troubleshooting
1. **App crashes on start**
	* Please enable the camera access for this app in the phone settings. 
