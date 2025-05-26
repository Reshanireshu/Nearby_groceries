import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Image,
  FlatList,
  SafeAreaView,
} from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';
import FontAwesome from 'react-native-vector-icons/FontAwesome';

const products = [
  {
    id: '1',
    name: 'Apple',
    price: '₹42/Kg',
    discount: '58',
    image: require('@/assets/images/apples.jpg'),
    liked: true,
  },
  {
    id: '2',
    name: 'Green apple',
    price: '₹65/Kg',
    discount: '35',
    image: require('@/assets/images/greenapple.jpg'),
    liked: false,
  },
  {
    id: '3',
    name: 'Orange',
    price: '₹41/500g',
    discount: '80',
    image: require('@/assets/images/orange.jpg'),
    liked: true,
  },
  {
    id: '4',
    name: 'Grapes',
    price: '₹19/500g',
    discount: '72',
    image: require('@/assets/images/grapes.jpg'),
    liked: false,
  },
  {
    id: '5',
    name: 'Mangoes',
    price: '₹72/Kg',
    discount: '20',
    image: require('@/assets/images/mango.jpg'),
    liked: false,
  },
  {
    id: '6',
    name: 'Banana',
    price: '₹42/500g',
    discount: '28',
    image: require('@/assets/images/banana.jpg'),
    liked: false,
  },
  {
    id: '7',
    name: 'Watermelon',
    price: '₹30/500g',
    discount: '40',
    image: require('@/assets/images/watermelon.jpg'),
    liked: false,
  },
  {
    id: '8',
    name: 'pineapple',
    price: '₹40/500g',
    discount: '30',
    image: require('@/assets/images/pineapple.jpg'),
    liked: false,
  },
  {
    id: '9',
    name: 'Kiwi',
    price: '₹40/500g',
    discount: '30',
    image: require('@/assets/images/kiwi.jpg'),
    liked: false,
  },
   {
    id: '10',
    name: 'Pomegranate',
    price: '₹39/500g',
    discount: '35',
    image: require('@/assets/images/pomegranate.jpg'),
    liked: false,
  },
];

export default function VegetableScreen() {
  return (
    <SafeAreaView style={styles.container}>
     
      <View style={styles.header}>
        <TouchableOpacity>
          <Icon name="arrow-back" size={24} color="black" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Fruits</Text>
        <View style={{ width: 24 }} /> 
      </View>

      
      <View style={styles.searchBar}>
        <TextInput
          placeholder="search"
          placeholderTextColor="#aaa"
          style={styles.searchInput}
        />
        <Icon name="search" size={20} color="white" />
      </View>

      
      <FlatList
        data={products}
        keyExtractor={(item) => item.id}
        numColumns={2}
        contentContainerStyle={styles.grid}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <View style={styles.discountBadge}>
              <Text style={styles.discountText}>{item.discount}% OFF</Text>
            </View>
            <Image source={item.image} style={styles.productImage} />
            <TouchableOpacity style={styles.heartIcon}>
              <FontAwesome
                name={item.liked ? 'heart' : 'heart-o'}
                size={18}
                color={item.liked ? 'deeppink' : 'black'}
              />
            </TouchableOpacity>
            <Text style={styles.productName}>{item.name}</Text>
            <Text style={styles.price}>{item.price}</Text>
            <TouchableOpacity style={styles.cartIcon}>
              <Icon name="cart-outline" size={20} color="white" />
            </TouchableOpacity>
          </View>
        )}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    justifyContent: 'space-between',
    marginTop:40
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#556B2F',
  },
  searchBar: {
    backgroundColor: 'black',
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 16,
    borderRadius: 20,
    paddingHorizontal: 16,
    height: 50,
  },
  searchInput: {
    flex: 1,
    color: 'white',
    marginRight: 8,
  },
  grid: {
    padding: 10,
  },
  card: {
    backgroundColor: '#f8f8f8',
    borderRadius: 8,
    width: '47%',
    margin: '1.5%',
    padding: 9,
    alignItems: 'center',
    position: 'relative',
    
  },
  discountBadge: {
    backgroundColor: '#C7E62B',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderBottomRightRadius: 12,
    borderTopLeftRadius: 14,
    alignSelf: 'flex-start',
    marginTop:-10,
    marginLeft:-9,
    height:33

  },
  discountText: {
    fontWeight: 'bold',
    fontSize: 12,
    color: 'black',
    marginTop:5
  },
  productImage: {
    width: 220,
    height: 140,
    marginVertical: 8,
    resizeMode: 'contain',
    borderRadius: 15,
  },
  heartIcon: {
    position: 'absolute',
    top: 8,
    right: 8,
  },
  productName: {
    fontWeight: 'bold',
    fontSize: 14,
    textAlign: 'center',
  },
  price: {
    fontSize: 12,
    color: '#333',
  },
  cartIcon: {
    backgroundColor: '#C7E62B',
    padding: 6,
    borderRadius: 6,
    position: 'absolute',
    bottom: 8,
    right: 8,
  },
});
