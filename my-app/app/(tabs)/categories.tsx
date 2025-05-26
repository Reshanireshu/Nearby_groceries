import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Image,
  SafeAreaView,
} from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';
import FontAwesome from 'react-native-vector-icons/FontAwesome';

const offerImages = [
  require('@/assets/images/vegetable.jpg'),
  require('@/assets/images/fruity.jpg'),
  require('@/assets/images/meats.jpg'),
  require('@/assets/images/cooldrinks.jpg'),
  require('@/assets/images/milks.jpg'),
  require('@/assets/images/flours.jpg'),
];

const categoryData = [
  {
    title: 'Vegetables & Green Leaves',
    image: require('@/assets/images/vegetable.jpg'),
  },
  {
    title: 'Fruits',
    image: require('@/assets/images/fruity.jpg'),
  },
  {
    title: 'Meat',
    image: require('@/assets/images/meats.jpg'),
  },
  {
    title: 'Milk & Dairy products',
    image: require('@/assets/images/milky.jpg'),
  },
  {
    title: 'Drinks & Juices',
    image: require('@/assets/images/cooldrinks.jpg'),
  },
  {
    title: 'Ice creams',
    image: require('@/assets/images/icecream.jpg'),
  },
  {
    title: 'Atta,dal & millets',
    image: require('@/assets/images/flours.jpg'),
  },
];

export default function HomeScreen() {
  return (
    <SafeAreaView style={styles.container}>
     
      <View style={styles.header}>
        <Icon name="person-circle-outline" size={45} color="#556B2F" />
        <View style={{ marginLeft: 8, flex: 1 }}>
          <Text style={styles.deliveryText}>DELIVERY IN 8 minutes</Text>
          <Text style={styles.address}>Airport Road, Meenambakkam, Chennai   <FontAwesome name="caret-down" size={16} color="black" /></Text>
          
        </View>
        
      </View>

     
      <View style={styles.searchBar}>
        <TextInput
          placeholder="Search"
          style={styles.searchInput}
          placeholderTextColor="#aaa"
        />
        <Icon name="search" size={22} color="white" />
      </View>

      <ScrollView showsVerticalScrollIndicator={false}>
        
        <Text style={styles.sectionTitle}>Offer Zone</Text>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.offerScroll}
        >
          {offerImages.map((img, idx) => (
            <View key={idx} style={styles.offerCard}>
              <Image source={img} style={styles.offerImage} />
              <Text style={styles.offerText}>{50 - idx * 5}% OFF</Text>
            </View>
          ))}
        </ScrollView>

        
        <Text style={styles.sectionTitle}>All Category</Text>
        {categoryData.map((item, idx) => (
          <View key={idx} style={styles.categoryCard}>
            <Image source={item.image} style={styles.categoryImage} />
            <View style={styles.categoryInfo}>
              <Text style={styles.categoryTitle}>{item.title}</Text>
              <TouchableOpacity style={styles.buyButton}>
                <Text style={styles.buyText}>Buy now</Text>
              </TouchableOpacity>
            </View>
          </View>
        ))}
      </ScrollView>

     
      <View style={styles.bottomNav}>
        {[
          { name: 'home', icon: 'home' },
          { name: 'category', icon: 'grid-outline' },
          { name: 'my cart', icon: 'cart-outline' },
          { name: 'user', icon: 'person-outline' },
          { name: 'more', icon: 'ellipsis-horizontal' },
        ].map((item, index) => (
          <TouchableOpacity key={index} style={styles.navItem}>
            <Icon name={item.icon} size={22} color="white" />
            <Text style={styles.navText}>{item.name}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'white' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: '#fff',
    elevation: 3,
    marginTop:50
  },
  deliveryText: {
    color: '#556B2F',
    fontWeight: 'bold',
    fontSize: 12,
    marginTop:10
    
  },
  address: {
    fontSize: 10,
    color: '#666',
  },
  searchBar: {
    margin: 15,
    backgroundColor: 'black',
    borderRadius: 20,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    height: 45,
  },
  searchInput: {
    flex: 1,
    color: 'white',
    marginRight: 10,
  },
  sectionTitle: {
    marginLeft: 12,
    marginTop: 20,
    fontWeight: 'bold',
    fontSize: 16,
  },
  offerScroll: {
    paddingHorizontal: 10,
    paddingTop: 10,
  },
  offerCard: {
    width: 130,
    height: 130,
    marginRight: 12,
    borderRadius: 10,
    overflow: 'hidden',
    position: 'relative',
  },
  offerImage: {
    width: '100%',
    height: '100%',
    borderRadius: 10,
  },
  offerText: {
    position: 'absolute',
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.6)',
    color: 'white',
    fontWeight: 'bold',
    padding: 6,
    fontSize: 18,
    textAlign: 'center',
    width: '100%',
  },
  categoryCard: {
    backgroundColor: '#fff',
    marginHorizontal: 12,
    marginTop: 10,
    marginBottom: 16,
    borderRadius: 10,
    elevation: 3,
  },
  categoryImage: {
    width: '100%',
    height: 180,
    borderTopLeftRadius: 10,
    borderTopRightRadius: 10,
  },
  categoryInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 10,
  },
  categoryTitle: {
    fontWeight: 'bold',
    fontSize: 14,
    flex: 1,
  },
  buyButton: {
    backgroundColor: '#C7E62B',
    borderRadius: 6,
    paddingVertical: 6,
    paddingHorizontal: 12,
  },
  buyText: {
    fontWeight: 'bold',
    fontSize: 12,
  },
  bottomNav: {
    flexDirection: 'row',
    backgroundColor: '#C7E62B',
    justifyContent: 'space-around',
    paddingVertical: 10,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  navItem: {
    alignItems: 'center',
  },
  navText: {
    fontSize: 12,
    marginTop: 4,
    textTransform: 'capitalize',
    color:'black',

  },
});
