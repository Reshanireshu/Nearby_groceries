import React from 'react';
import {
  ImageBackground,
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Image,
} from 'react-native';

export default function HomeScreen({ navigation }) {
  return (
    <ImageBackground
      source={require('@/assets/images/background.jpg')}
      style={styles.container}
      resizeMode="cover"
    >
      <Image
        source={require('@/assets/images/fruit.jpg')}
        style={styles.headerImage}
        resizeMode="cover"
      />

      <View style={styles.content}>
        <Text style={styles.title}>NEARBY</Text>
        <Text style={styles.tagline}>
          <Text style={styles.italicBold}>freshness on your doorstep</Text>
        </Text>
        <Text style={styles.paragraph}>
          Congratulations for choosing us for a better grocery shopping experience. We not only offer the best products — we also deliver them to you!
        </Text>

        <TouchableOpacity
          style={styles.button}
          onPress={() => navigation.navigate('Explore')}
        >
          <Text style={styles.arrow}>➔</Text>
        </TouchableOpacity>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  headerImage: {
    height: 280,
    width: '110%',
    borderBottomLeftRadius: 240,
    borderBottomRightRadius: 210,
    overflow: 'hidden',
    alignSelf: 'center',
    marginLeft: -20,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 30,
    alignItems: 'center',
  },
  title: {
    fontSize: 48,
    fontWeight: 'bold',
    color: 'white',
    marginTop: 10,
    textAlign: 'center',
  },
  tagline: {
    fontSize: 18,
    marginTop: -6,
    color: 'black',
    textAlign: 'center',
  },
  italicBold: {
    fontWeight: 'bold',
    fontStyle: 'italic',
  },
  paragraph: {
    marginTop: 15,
    fontSize: 15,
    textAlign: 'center',
    color: 'black',
    paddingHorizontal: 10,
  },
  button: {
    marginTop: 60,
    backgroundColor: '#C7E62B',
    width: 60,
    height: 60,
    borderRadius: 30,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: 'black',
  },
  arrow: {
    fontSize: 24,
    fontWeight: 'bold',
  },
});
