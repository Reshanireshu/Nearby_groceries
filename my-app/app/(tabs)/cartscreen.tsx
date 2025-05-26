import React, { useState } from 'react';
import { View, Text, Image, TouchableOpacity, ScrollView, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const CartScreen = () => {
  const [quantity, setQuantity] = useState(1); 

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={true}>
     
      <View style={styles.header}>
        <Ionicons name="arrow-back" size={24} color="#000" />
        <Text style={styles.headerTitle}>Your Cart</Text>
      </View>

      
      <View style={styles.savingsBanner}>
        <Text style={styles.savingsText}>₹45 SAVINGS ON THIS ORDER WITH</Text>
        <Image source={require('@/assets/images/supersaver.jpg')} style={styles.superSaverIcon} />
      </View>

      
      <TouchableOpacity style={styles.row}>
        <Ionicons name="pricetags-outline" size={20} color="#000" />
        <Text style={styles.rowText}>View Coupons & Offers</Text>
        <Ionicons name="chevron-forward" size={20} color="#000" />
      </TouchableOpacity>

      
      <View style={styles.deliveryBlock}>
        <View style={styles.row}>
          <Image source={require('@/assets/images/clock.jpg')} style={styles.iconImage} />
          <Text style={styles.deliveryText}>Delivery in 10 mins</Text>
        </View>
        <View style={styles.itemCard}>
          <Image source={require('@/assets/images/tomato.jpg')} style={styles.itemImage} />
          <View style={{ flex: 1 }}>
            <Text style={styles.itemName}>Tomato</Text>
            <Text style={styles.itemWeight}>500 g</Text>
            <View style={styles.qtyPriceRow}>
              <View style={styles.qtyControl}>
                <TouchableOpacity onPress={() => setQuantity(prev => Math.max(1, prev - 1))}>
                  <Text style={styles.qtyBtn}>-</Text>
                </TouchableOpacity>
                <Text style={styles.qtyNum}>{quantity}</Text>
                <TouchableOpacity onPress={() => setQuantity(prev => prev + 1)}>
                  <Text style={styles.qtyBtn}>+</Text>
                </TouchableOpacity>
              </View>
              <View style={{ alignItems: 'flex-end' }}>
                <Text style={styles.itemPrice}>₹153.78</Text>
                <Text style={styles.itemMRP}>₹194</Text>
              </View>
            </View>
          </View>
        </View>
        <TouchableOpacity style={styles.addMoreBtn}>
          <Text style={styles.addMoreText}>+ Add More Items</Text>
        </TouchableOpacity>
      </View>

      
      <Text style={styles.suggestionTitle}>You might also like</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.suggestionScroll}>
        {[
          {
            name: 'Milk',
            price: '₹166.68',
            mrp: '₹283',
            off: '₹116',
            image: require('@/assets/images/milk.jpg')
          },
          {
            name: 'Carrot',
            price: '₹24',
            mrp: '₹82',
            off: '₹58',
            image: require('@/assets/images/carrot.jpg')
          },
          {
            name: 'Apples',
            price: '₹42.71',
            mrp: '₹74',
            off: '₹31',
            image: require('@/assets/images/apples.jpg')
          },
          {
            name: 'Chillies',
            price: '₹22',
            mrp: '₹47',
            off: '₹25',
            image: require('@/assets/images/chillies.jpg'),
          },
          {
            name: 'Pineapple',
            price: '₹58.88',
            mrp: '₹102',
            off: '₹43',
            image: require('@/assets/images/pineapple.jpg'),
          },
          {
            name: 'Brinjal',
            price: '₹25.56',
            mrp: '₹62',
            off: '₹36',
            image: require('@/assets/images/brinjal.jpg'),
          },
          {
            name: 'Watermelon',
            price: '₹60.5',
            mrp: '₹146',
            off: '₹86',
            image: require('@/assets/images/watermelon.jpg'),
          },
          {
            name: 'Fiber',
            price: '₹26.62',
            mrp: '₹48',
            off: '₹21',
            image: require('@/assets/images/flours.jpg'),
          },
          {
            name: 'Banana',
            price: '₹16',
            mrp: '₹55',
            off: '₹39',
            image: require('@/assets/images/banana.jpg'),
          },

        ].map((item, idx) => (
          <View key={idx} style={styles.suggestionCard}>
            <View style={styles.suggestionPriceTag}>
              <Text style={styles.suggestionPrice}>{item.price}</Text>
              <Text style={styles.suggestionMRP}>MRP {item.mrp}</Text>
            </View>
            <Image source={item.image} style={styles.suggestionImage} />
            <View style={styles.suggestionBottom}>
              <Ionicons name="time-outline" size={12} color="#555" />
              <Text style={styles.suggestionDelivery}>10 Mins</Text>
            </View>
            <Text style={styles.suggestionName}>{item.name}</Text>
            <View style={styles.suggestionOffTag}>
              <Text style={styles.suggestionOffText}>{item.off} off</Text>
            </View>
            <TouchableOpacity style={styles.suggestionAddBtn}>
              <Text style={styles.suggestionAddText}>Add to Cart</Text>
            </TouchableOpacity>
          </View>
        ))}
      </ScrollView>
      
            <View style={styles.summaryBlock}>
            
            <TouchableOpacity style={styles.seeAllBtn}>
                <Text style={styles.seeAllText}>See all products</Text>
            </TouchableOpacity>

            
            <View style={styles.userInfoRow}>
                <Text style={styles.userText}>Ordering for <Text style={{ color: '#d0006f' }}>Lincy</Text>,{'\n'}{'\n'}9786293890</Text>
                <TouchableOpacity>
                <Text style={styles.editText}>Edit</Text>
                </TouchableOpacity>
            </View>

           
            <View style={styles.deliveryFreeRow}>
                <Text style={styles.freeDeliveryText}>• Free delivery on this order</Text>
                <TouchableOpacity style={styles.applyBtn}>
                <Text style={styles.applyText}>APPLY</Text>
                </TouchableOpacity>
            </View>

           
            {[
                {
                icon: 'wallet-outline',
                title: 'Delivery Partner Tip',
                subtitle: 'This amount goes to your delivery partner',
                },
                {
                icon: 'document-text-outline',
                title: 'Delivery Instructions',
                subtitle: 'Delivery partner will be notified',
                },
                {
                icon: 'cash-outline',
                title: 'To Pay',
                subtitle: 'Incl. all taxes and charges',
                price: '₹204',
                mrp: '₹249',
                saving: '₹45.23',
                },
                {
                icon: 'shield-checkmark-outline',
                title: "Delivery Partner's Safety",
                subtitle: 'Learn more about how we ensure their safety',
                }
            ].map((item, idx) => (
                <TouchableOpacity key={idx} style={styles.infoRow}>
                <Ionicons name ={item.icon} size={20} color="#555" />
                <View style={{ flex: 1, marginLeft: 10 }}>
                    <Text style={styles.infoTitle}>{item.title}</Text>
                    <Text style={styles.infoSubtitle}>{item.subtitle}</Text>
                </View>
                {item.price && (
                    <View style={{ alignItems: 'flex-end' }}>
                    <Text style={styles.infoPrice}>{item.price}</Text>
                    <Text style={styles.infoMRP}>₹{item.mrp}</Text>
                    <Text style={styles.infoSaving}>SAVING ₹{item.saving}</Text>
                    </View>
                )}
                <Ionicons name="chevron-forward" size={20} color="#888" />
                </TouchableOpacity>
            ))}
            </View>

        <View style={styles.footer}>
            <View style={styles.addressContainer}>
            <Ionicons name="location-outline" size={20} color="#555" />
            <Text style={styles.addressText}>17th A Main Road, 6th Block, Koramangala...</Text>
            </View>
            <TouchableOpacity style={styles.payButton}>
            <Text style={styles.payText}>Click to Pay</Text>
            </TouchableOpacity>
        </View>
    </ScrollView>
  );
};

export default CartScreen;

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  header: { flexDirection: 'row', alignItems: 'center', padding: 15 },
  headerTitle: { fontSize: 18, fontWeight: 'bold', marginTop: 50 },

  savingsBanner: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#00A000',
    padding: 12,
    marginHorizontal: 10,
    borderRadius: 10,
    marginBottom: 10,
  },
  savingsText: { color: 'white', fontWeight: 'bold' },
  superSaverIcon: { width: 80, height: 25, resizeMode: 'contain' },

  row: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    justifyContent: 'space-between',
    borderBottomWidth: 1,
    borderColor: '#eee',
  },
  rowText: { fontSize: 16, flex: 1, marginLeft: 10 },

  deliveryBlock: { padding: 15},
  deliveryText: { fontWeight: 'bold', marginRight: 130,marginTop:-10, fontSize:16 },
  itemCard: {
    flexDirection: 'row',
    marginTop: 10,
    padding: 10,
    backgroundColor: '#f9f9f9',
    borderRadius: 10,
  },
  itemImage: { width: 50, height: 50, borderRadius: 6, marginRight: 10 },
  iconImage: { width: 50, height: 50, borderRadius: 6, marginRight: 10, marginTop:-20},
  itemName: { fontWeight: 'bold' },
  itemWeight: { fontSize: 12, color: '#777' },
  qtyPriceRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 10 },
  qtyControl: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  qtyBtn: { fontSize: 16, paddingHorizontal: 6 },
  qtyNum: { fontSize: 16, marginHorizontal: 4 },
  itemPrice: { fontWeight: 'bold' },
  itemMRP: { textDecorationLine: 'line-through', fontSize: 12, color: '#999' },

  addMoreBtn: {
    marginTop: 10,
    backgroundColor: '#000',
    padding: 10,
    borderRadius: 6,
    alignItems: 'center',
  },
  addMoreText: { color: '#fff', fontWeight: 'bold' },

  suggestionTitle: { fontSize: 16, fontWeight: 'bold', marginHorizontal: 15, marginTop: 10 },
  suggestionScroll: { paddingHorizontal: 15, paddingVertical: 10 },
  suggestionCard: {
    width: 120,
    marginRight: 10,
    backgroundColor: '#fff',
    borderRadius: 10,
    elevation: 2,
    padding: 10,
    alignItems: 'center',
  },
  suggestionImage: { width: 80, height: 60, resizeMode: 'cover', borderRadius: 5, marginVertical: 5 },
  suggestionPriceTag: { alignItems: 'center' },
  suggestionPrice: { fontWeight: 'bold', fontSize: 14, color: '#d00000' },
  suggestionMRP: { fontSize: 12, color: '#999', textDecorationLine: 'line-through' },
  suggestionDelivery: { fontSize: 10, color: '#555', marginLeft: 4 },
  suggestionName: { fontSize: 13, marginTop: 5, textAlign: 'center' },
  suggestionBottom: { flexDirection: 'row', alignItems: 'center', marginTop: 5 },
  suggestionOffTag: {
    backgroundColor: 'green',
    paddingHorizontal: 5,
    paddingVertical: 2,
    borderRadius: 10,
    marginTop: 5,
  },
  suggestionOffText: { color: '#fff', fontSize: 11 },
  suggestionAddBtn: {
    backgroundColor: '#FF1493',
    paddingVertical: 5,
    paddingHorizontal: 8,
    borderRadius: 6,
    marginTop: 8,
  },
  suggestionAddText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },

  footer: {
    borderTopWidth: 1,
    borderColor: '#eee',
    padding: 15,
    backgroundColor: '#fff',
  },
  addressContainer: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  addressText: { marginLeft: 5, fontSize: 12, color: '#555' },
  payButton: {
    backgroundColor: '#FF1493',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  payText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  summaryBlock: {
  backgroundColor: '#fff',
  marginHorizontal: 10,
  borderRadius: 10,
  padding: 10,
  marginBottom: 20,
  marginTop: 10,
  elevation: 2,
},

seeAllBtn: {
  backgroundColor: '#ffe6f0',
  padding: 10,
  borderRadius: 8,
  alignItems: 'center',
  marginBottom: 10,
},
seeAllText: { color: '#d0006f', fontWeight: 'bold' },

userInfoRow: {
  flexDirection: 'row',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: 10,
},
userText: { fontSize: 14, color: '#000' },
editText: { color: '#d0006f', fontWeight: 'bold' },

deliveryFreeRow: {
  flexDirection: 'row',
  justifyContent: 'space-between',
  alignItems: 'center',
  backgroundColor: '#f8f2ff',
  borderRadius: 8,
  padding: 10,
  marginBottom: 10,
},
freeDeliveryText: { 
    color: '#a000d0', 
    fontWeight: 'bold',
    
 },
applyBtn: {
  backgroundColor: '#ffebf0',
  paddingHorizontal: 12,
  paddingVertical: 5,
  borderRadius: 20,
},
applyText: { color: '#d0006f', fontWeight: 'bold' },

infoRow: {
  flexDirection: 'row',
  alignItems: 'center',
  paddingVertical: 12,
  borderBottomWidth: 1,
  borderColor: '#eee',
},
infoTitle: { fontWeight: 'bold', fontSize: 14 },
infoSubtitle: { fontSize: 12, color: '#555' },
infoPrice: { fontWeight: 'bold', color: '#000' },
infoMRP: { textDecorationLine: 'line-through', fontSize: 12, color: '#aaa' },
infoSaving: { color: 'green', fontSize: 12 },

});
