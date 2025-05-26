import React, { useState } from 'react';
import {View,Text,TextInput,StyleSheet,Image,TouchableOpacity,SafeAreaView,} from 'react-native';

export default function OtpScreen() {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [error, setError] = useState(false);

  const handleContinue = () => {
  if (phoneNumber.trim() === '') {
    setError(true);
  } else {
    setError(false);
    
  }
};

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
        source={require('@/assets/images/otp.jpg')} 
        style={styles.illustration}
        resizeMode="contain"
      />

      <Text style={styles.heading}>OTP Verification</Text>
      <Text style={styles.subtext}>
        Enter phone number to send{'\n'}one time password
      </Text>

      <Text style={styles.label}>Phone Number</Text>

<View style={[styles.inputContainer, error && styles.errorBorder]}>
  <TextInput
    placeholder="+91-"
    keyboardType="phone-pad"
    value={phoneNumber}
    onChangeText={(text) => {
      setPhoneNumber(text);
      if (text.trim() !== '') setError(false);
    }}
    style={styles.input}
  />
</View>

{error && (
 <Text style={styles.errorText}>Please enter your phone number</Text>
)}



      <TouchableOpacity style={styles.button} onPress={handleContinue}>
        <Text style={styles.buttonText}>Continue</Text>
      </TouchableOpacity>

    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
  flex: 1,
  backgroundColor: 'white',
  padding: 20,
  paddingTop: 10,
  minHeight: 800, 
},

  illustration: {
    width: '100%',
    height: 380,
    marginTop: -30,
  },
  heading: {
    fontSize: 26,
    fontWeight: 'bold',
    color: '#C7E62B',
    textAlign: 'center',
    marginTop: -50,
  },
  subtext: {
    textAlign: 'center',
    color: 'black',
    fontSize: 14,
    marginVertical: 8,
  },
  label: {
    fontWeight: 'bold',
    fontSize: 16,
    color: '#C7E62B',
    marginTop: 20,
    marginBottom: 5,
    textAlign: 'center',
  },
  inputContainer: {
    backgroundColor: '#fff',
    borderRadius: 15,
    borderWidth: 1.5,
    borderColor: 'black',
    paddingHorizontal: 15,
    paddingVertical: 10,
    marginVertical: 5,
  },
  input: {
    fontSize: 16,
    color: 'black',
  },
  button: {
    backgroundColor: 'black',
    paddingVertical: 15,
    borderRadius: 10,
    marginTop: 30,
    alignItems: 'center',
  },
  buttonText: {
    color: '#C7E62B',
    fontWeight: 'bold',
    fontSize: 16,
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
  errorBorder: {
  borderColor: 'red',
},
errorText: {
  color: 'red',
  fontSize: 13,
  marginTop: 4,
  textAlign: 'center',
},

});
