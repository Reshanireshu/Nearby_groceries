import React from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  Image,
  SafeAreaView,
} from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons'; // or any other icon library

const locations = [
  {
    name: 'Perimet',
    address: 'Poongavanapuram, Chennai, Tamil Nadu',
  },
  {
    name: 'Chennai',
    address: 'Chennai, Tamil Nadu, India',
  },
  {
    name: 'Chennai International Airport (MAA)',
    address:
      'Chennai International Airport (MAA), Airport Road, Meenambakkam, Chennai,...',
  },
  {
    name: 'Chennai Central',
    address: 'Chennai Central, Tamil Nadu',
  },
  {
    name:'Chennaimalai',
    address:'Chennaimalai,Tmail Nadu India'
  },
   {
    name:'Chennai One IT SEZ',
    address:'Chennai One IT SEZ,MZN Nagar Extension,Thoraipakkam,Tmail Nadu India'
  },
];

export default function LocationScreen({ navigation }) {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.statusBar}>
              <Text style={styles.time}>9:30</Text>
              <View style={styles.statusIcons}>
                <Image source={require('@/assets/images/wifi.png')} style={styles.statusIcon} />
                <Image source={require('@/assets/images/signal.png')} style={styles.statusIcon} />
                <Image source={require('@/assets/images/charge.png')} style={styles.statusIcon} />
              </View>
      </View>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Icon name="arrow-back" size={24} color="black" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>your location</Text>
      </View>

      
      <View style={styles.searchBar}>
        <Icon name="menu" size={18} color="#fff" />
        <TextInput placeholder="search" placeholderTextColor="#ccc" style={styles.input} />
        <Icon name="search" size={18} color="#fff" />
      </View>

      
      <TouchableOpacity style={styles.currentLocation}>
        <Text style={styles.currentLocationText}>Current Location</Text>
      </TouchableOpacity>

      
      <FlatList
        data={locations}
        keyExtractor={(item, index) => index.toString()}
        renderItem={({ item }) => (
          <View style={styles.locationItem}>
            <Image
              source={require('@/assets/images/pin.jpg')} 
              style={styles.locationIcon}
            />
            <View style={styles.locationText}>
              <Text style={styles.locationName}>{item.name}</Text>
              <Text style={styles.locationAddress}>{item.address}</Text>
            </View>
          </View>
        )}
      />
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    paddingHorizontal: 20,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#C7E62B',
    marginLeft: 70,
    marginTop:40,
    textTransform: 'lowercase',
  },
  searchBar: {
    flexDirection: 'row',
    backgroundColor: 'black',
    borderRadius: 30,
    alignItems: 'center',
    paddingHorizontal: 20,
    marginTop: 20,
    height: 50,
  },
  input: {
    flex: 1,
    color: 'white',
    marginHorizontal: 10,
  },
  currentLocation: {
    backgroundColor: 'black',
    borderRadius: 30,
    marginTop: 20,
    alignItems: 'center',
    justifyContent: 'center',
    height: 50,
    marginBottom:50
  },
  currentLocationText: {
    color: '#C7E62B',
    fontWeight: 'bold',
    fontSize: 16,
  },
  locationItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderColor: '#ddd',
  },
  locationIcon: {
    width: 20,
    height: 20,
    marginTop: 5,
    marginRight: 10,
  },
  locationText: {
    flex: 1,
  },
  locationName: {
    fontWeight: 'bold',
    fontSize: 16,
    color: '#000',
  },
  locationAddress: {
    color: '#777',
    marginTop: 2,
  },
  statusBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    paddingHorizontal: 10,
    marginTop: 20,
    alignItems: 'center',
  },
  time: {
    fontSize: 13,
    fontWeight: 'bold',
    color: 'black',
    marginTop:40
  },
  statusIcons: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIcon: {
    width: 18,
    height: 18,
    marginLeft: 6,
    marginTop:40,
    resizeMode: 'contain',
  },
});
