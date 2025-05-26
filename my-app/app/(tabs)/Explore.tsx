import React from 'react';
import {View,Text,StyleSheet,TouchableOpacity,Image,ScrollView,} from 'react-native';

export default function ExploreScreen() {
  return (
    <ScrollView contentContainerStyle={styles.scrollContainer}>
      
      
      <View style={styles.statusBar}>
        <Text style={styles.time}>9:30</Text>
        <View style={styles.statusIcons}>
          <Image source={require('@/assets/images/wifi.png')} style={styles.statusIcon} />
          <Image source={require('@/assets/images/signal.png')} style={styles.statusIcon} />
          <Image source={require('@/assets/images/charge.png')} style={styles.statusIcon} />
        </View>
      </View>

      
      <View style={styles.container}>
        <Text style={styles.heading}>
          <Text style={styles.select}>select</Text>
        </Text>
        <Text style={styles.heading1}>
          <Text style={styles.userType}>user type</Text>
        </Text>
        <Text style={styles.subtext}>
          Select the user type that {'\n'}represents you
        </Text>

        <TouchableOpacity style={[styles.option, styles.customer]}>
          <Image source={require('@/assets/images/customer.jpg')} style={styles.icon} />
          <Text style={styles.optionText}> Customer</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.option, styles.shopkeeper]}>
          <Image source={require('@/assets/images/shopkeeper.jpg')} style={styles.icon} />
          <Text style={styles.optionText}>Shop keeper</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.option, styles.delivery]}>
          <Image source={require('@/assets/images/delivery.jpg')} style={styles.icon} />
          <Text style={styles.optionText}>Delivery partner</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.option, styles.continue]}>
          <Text style={styles.optionsText}>Continue</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scrollContainer: {
    flexGrow: 1,
    backgroundColor: 'white',
    padding: 20,
    paddingTop: 10,
    height:1000
  },
  statusBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 5,
    marginBottom: 10,
  },
  time: {
    fontSize: 13,
    fontWeight: 'bold',
    color: 'black',
    marginLeft:-10,
    marginTop:50
  },
  statusIcons: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIcon: {
    width: 18,
    height: 18,
    marginLeft: 6,
    marginTop:50,
    resizeMode: 'contain',
  },
  container: {
    alignItems: 'center',
    width: '100%',
  },
  heading: {
    fontSize: 47,
    fontWeight: 'bold',
    marginRight: 210,
    textAlign: 'center',
    lineHeight: 40,
    marginTop: 10,
  },
  heading1: {
    fontSize: 40,
    fontWeight: 'bold',
    marginLeft: -160,
   
  },
  select: {
    color: '#C7E62B',
    textShadowOffset: { width: 3, height: 5 },
    textShadowRadius: 1,
  },
  userType: {
    color: '#333',
    textShadowOffset: { width: 3, height: 5 },
    textShadowRadius: 1,
  },
  subtext: {
    fontSize: 16,
    color: '#666',
    marginTop: -5,
    textAlign: 'center',
    marginLeft: -130,
  },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ccc',
    padding: 20,
    borderRadius: 20,
    width: '100%',
    height: 90,
    marginTop: 10,
  },
  customer: {
    backgroundColor: '#C7E62B',
    marginTop: 90,
  },
  shopkeeper: {
    marginTop: 30,
  },
  delivery: {
    marginTop: 30,
  },
  icon: {
    width: 100,
    height: 75,
    resizeMode: 'cover',
    borderRadius: 10,
    marginLeft: -13,
  },
  optionText: {
    fontSize: 18,
    color: 'white',
    fontWeight: '600',
  },
  continue: {
    backgroundColor: 'black',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 60,
  },
  optionsText: {
    color: '#C7E62B',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    width: '100%',
  },
});
