import React from 'react';
import { View, Text, Image, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons, AntDesign, FontAwesome } from '@expo/vector-icons';

const ProductDetail = () => {
  return (
    <View style={styles.container}>
      <ScrollView>
        
        <View style={styles.header}>
          <TouchableOpacity>
            <Ionicons name="arrow-back" size={24} color="white" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Fresh onion (small)</Text>
          <TouchableOpacity>
            <AntDesign name="hearto" size={23} color="white" />
          </TouchableOpacity>
        </View>

       
        <Image source={require('@/assets/images/onion.jpg')} style={styles.image} />

       
        <TouchableOpacity style={styles.shareIcon}>
          <FontAwesome name="share-alt" size={22} color="white" />
        </TouchableOpacity>

        
        <View style={styles.card}>
          <View style={styles.titleRow}>
            <Text style={styles.productTitle}>Fresh onion</Text>
            <View style={styles.rating}>
              <Text style={styles.ratingText}>4.5</Text>
              <AntDesign name="star" size={14} color="black" />
            </View>
          </View>
          <Text style={styles.subtitle}>(small)</Text>
          <Text style={styles.oldPrice}>1 kg ₹100</Text>
          <Text style={styles.discount}>35% OFF</Text>
          <Text style={styles.price}>₹65/Kg</Text>
        </View>

       
        <View style={styles.description}>
          <Text style={styles.sectionTitle}>Description</Text>
          <Text style={styles.text}>
            The big onion is a staple ingredient, known for its sweet and savory flavour. Its large size and firm texture make it perfect for slicing, chopping, or caramelizing. The onion adds depth to soups, stews, salads, and more. Papery skin is typically golden or yellow, while the flesh is white or translucent.
          </Text>
        </View>

        
        <View style={styles.description}>
          <Text style={styles.sectionTitle}>Health benefits</Text>
          <Text style={styles.text}>
            Rich in fiber, antioxidants, and various essential vitamins and minerals.
          </Text>
        </View>

        <View style={styles.description}>
          <Text style={styles.relatedItems}>Related items</Text>
        </View>

        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.relatedScroll}>
          <View style={styles.relatedCard}>
            <Text style={styles.discountTag}>58% OFF</Text>
            <Image source={require('@/assets/images/freshonion.jpg')} style={styles.relatedImage} />
            <AntDesign name="heart" size={18} color="deeppink" style={styles.heartIcon} />
            <Text style={styles.relatedTitle}>Fresh onion</Text>
            <Text style={styles.relatedPrice}>₹42/Kg</Text>
            <TouchableOpacity style={styles.cartIcon}>
              <Ionicons name="cart-outline" size={20} color="white" />
            </TouchableOpacity>
          </View>

          <View style={styles.relatedCard}>
            <Text style={styles.discountTag}>80% OFF</Text>
            <Image source={require('@/assets/images/tomato.jpg')} style={styles.relatedImage} />
            <AntDesign name="heart" size={18} color="deeppink" style={styles.heartIcon} />
            <Text style={styles.relatedTitle}>Tomato</Text>
            <Text style={styles.relatedPrice}>₹41/500g</Text>
            <TouchableOpacity style={styles.cartIcon}>
              <Ionicons name="cart-outline" size={20} color="white"/>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </ScrollView>

      
      <TouchableOpacity style={styles.addButton}>
        <Text style={styles.addButtonText}>Add to cart</Text>
      </TouchableOpacity>
    </View>
  );
};

export default ProductDetail;


const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    paddingTop: 40,
    paddingHorizontal: 15,
    backgroundColor: '#72003B',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingBottom: 10,
  },
  headerTitle: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  image: {
    width: '100%',
    height: 180,
    resizeMode: 'contain',
    backgroundColor: '#72003B',
    
  },
  shareIcon: {
    position: 'absolute',
    top: 180,
    right: 20,
  },
  card: {
    margin: 10,
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    elevation: 5,
  },
  titleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  productTitle: {
    fontSize: 22,
    fontWeight: 'bold',
  },
  rating: {
    flexDirection: 'row',
    backgroundColor: '#FFD700',
    padding: 4,
    borderRadius: 5,
    alignItems: 'center',
  },
  ratingText: {
    marginRight: 4,
    fontWeight: 'bold',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginVertical: 4,
  },
  oldPrice: {
    textDecorationLine: 'line-through',
    color: '#888',
    marginVertical: 2,
  },
  discount: {
    color: 'green',
    fontWeight: 'bold',
  },
  price: {
    fontSize: 18,
    color: 'green',
    fontWeight: 'bold',
    marginTop: 4,
  },
  description: {
    marginHorizontal: 15,
    marginTop: 10,
  },
  sectionTitle: {
    fontWeight: 'bold',
    color: 'green',
    fontSize: 16,
    marginBottom: 4,
  },
  text: {
    fontSize: 14,
    color: '#333',
  },
  relatedItems: {
    fontWeight: 'bold',
    color: 'green',
    fontSize: 16,
    
  },
  relatedScroll: {
    paddingLeft: 10,
    marginTop: 10,
    marginBottom: 20,
  },
  relatedCard: {
    backgroundColor: '#f8f8f8',
    width: 150,
    borderRadius: 10,
    padding: 10,
    marginRight: 12,
    alignItems: 'center',
    position: 'relative',
  },
  relatedImage: {
    width: 100,
    height: 80,
    resizeMode: 'contain',
    marginTop: 30,
  },
  discountTag: {
    position: 'absolute',
    top: 5,
    left: 5,
    backgroundColor: '#DFFF00',
    paddingHorizontal: 6,
    paddingVertical: 2,
    fontSize: 12,
    fontWeight: 'bold',
    borderRadius: 4,
  },
  heartIcon: {
    position: 'absolute',
    top: 5,
    right: 5,
  },
  relatedTitle: {
    fontWeight: 'bold',
    fontSize: 14,
    marginTop: 5,
  },
  relatedPrice: {
    fontSize: 13,
    color: 'green',
    marginVertical: 4,
  },
  cartIcon: {
    backgroundColor: '#DFFF00',
    padding: 6,
    borderRadius: 6,
  },
  addButton: {
    backgroundColor: '#DFFF00',
    padding: 15,
    alignItems: 'center',
    borderTopWidth: 1,
    borderColor: '#ccc',
  },
  addButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#000',
  },
});
