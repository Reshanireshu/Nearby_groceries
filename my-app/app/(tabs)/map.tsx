import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView } from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';

export default function LocationInfoScreen({ navigation }) {
  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Icon name="arrow-back" size={28} color="black" />
        </TouchableOpacity>
        <Text style={styles.title}>Location Information</Text>
        <View style={{ width: 28 }} /> {/* To balance spacing */}
      </View>

       <View style={styles.locationDetails}>
        <Text style={styles.locationHeading}>Perimet</Text>
        <Text style={styles.locationSub}>Poongavanapuram, Chennai</Text>
      </View>
      <TouchableOpacity style={styles.button} onPress={() => navigation.navigate('NextScreen')}>
        
        <Text style={styles.buttonText}>Confirm & Continue</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'white',
    paddingHorizontal: 20,
    justifyContent: 'space-between',
    paddingVertical: 40,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#C7E62B',
    marginTop:40
  },
  button: {
    backgroundColor: 'black',
    paddingVertical: 16,
    borderRadius: 10,
    alignItems: 'center',
  },
  buttonText: {
    color: '#C7E62B',
    fontSize: 16,
    fontWeight: 'bold',
  },
  text:{
    color:'black'
    
  },
  locationDetails: {
    marginTop: 100,
    alignItems: 'center',
  },
  locationHeading: {
    fontSize: 22,
    fontWeight: 'bold',
    color: 'black',
    marginTop:350,
    marginLeft:-250
  },
  locationSub: {
    fontSize: 14,
    color: 'gray',
    marginTop: -2,
    marginLeft:-140
  },
});
