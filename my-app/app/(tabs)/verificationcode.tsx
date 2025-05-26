import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  Image,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';

export default function CodeVerificationScreen({ navigation }) {
  const [code, setCode] = useState(['', '', '', '']);
  const inputRefs = useRef([]);


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

      
      <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backArrow}>
        <Icon name="arrow-back" size={28} color="black" />
      </TouchableOpacity>

      
      <Image
        source={require('@/assets/images/ver.jpg')}
        style={styles.image}
        resizeMode="contain"
      />

      
      <Text style={styles.heading}>Verification Code</Text>
      <Text style={styles.subtext}>
        We have sent the{'\n'}verification code to your phone number
      </Text>

      
      <View style={styles.codeContainer}>
        {code.map((digit, index) => (
          <TextInput
            key={index}
            style={[styles.codeInput, index === 2 ? styles.activeBox : null]}
            keyboardType="numeric"
            maxLength={1}
            value={digit}
           
          />
        ))}
      </View>

     
      <TouchableOpacity>
        <Text style={styles.resend}>Resend OTP</Text>
      </TouchableOpacity>

      
      <TouchableOpacity style={[styles.option, styles.continue]}>
        <Text style={styles.optionsText}>Continue</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 24,
  },
  backArrow: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 5,
  },
  image: {
    width: '100%',
    height: 230,
    marginTop: -20,
  },
  heading: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#C7E62B',
    textAlign: 'center',
    marginVertical: 10,
  },
  subtext: {
    fontSize: 14,
    textAlign: 'center',
    color: 'black',
    marginBottom: 20,
  },
  codeContainer: {
    flexDirection: 'row',
    justifyContent: 'space-evenly',
    marginVertical: 20,
  },
  codeInput: {
    backgroundColor: 'black',
    color: 'white',
    fontSize: 22,
    borderRadius: 12,
    textAlign: 'center',
    width: 60,
    height: 60,
  },
  activeBox: {
    borderColor: '#C7E62B',
    borderWidth: 2,
  },
  resend: {
    textAlign: 'center',
    color: '#C7E62B',
    fontWeight: 'bold',
    marginTop: 10,
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
    marginTop: 20,
  },
  optionsText: {
    color: '#C7E62B',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    width: '100%',
  },
  statusBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 10,
    marginBottom: 10,
    paddingHorizontal: 10,
  },
  time: {
    fontSize: 14,
    fontWeight: 'bold',
    color: 'black',
    marginLeft: -10,
    marginTop: 20,
  },
  statusIcons: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIcon: {
    width: 18,
    height: 18,
    marginLeft: 6,
    marginTop: 20,
    resizeMode: 'contain',
  },
});
