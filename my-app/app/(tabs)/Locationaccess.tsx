import React from 'react';
import { View, Text, Image, StyleSheet, SafeAreaView, TouchableOpacity, } from 'react-native';

export default function SuccessScreen() {
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

      <Image
        source={require('@/assets/images/locationaccess.jpg')}
        style={styles.image}
        resizeMode="contain"
      />

      <Text style={styles.success}>Location Access</Text>
      <Text style={styles.message}>
       Please enable location access so we could provide you accurate results nearest grocery shops and store
      </Text>
      <TouchableOpacity style={[styles.option, styles.continue]}>
          <Text style={styles.optionsText}>Allow Access</Text>
      </TouchableOpacity>
    </SafeAreaView>
    
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    paddingHorizontal: 25,
    alignItems: 'center',
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
  image: {
    width: '200%',
    height: 300,
    marginVertical: 90,
    marginTop:30
  },
  success: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#C7E62B',
    marginBottom: 20,
    marginTop:-90
  },
  message: {
    fontSize: 16,
    color: 'black',
    textAlign: 'center',
    lineHeight: 22,
  },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ccc',
    padding: 20,
    borderRadius: 20,
    width: '100%',
    height: 90,
    marginTop: 15,
  },
  continue: {
    backgroundColor: 'black',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 100,
  },
  optionsText: {
    color: '#C7E62B',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    width: '100%',
  },
});
