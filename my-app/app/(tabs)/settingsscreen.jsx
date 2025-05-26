import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const SettingsScreen = () => {
  const [preference, setPreference] = useState(null);

  return (
    <ScrollView style={styles.container}>
      <TouchableOpacity style={styles.backIcon}>
        <Ionicons name="arrow-back" size={24} color="black" />
      
      
      <Text style={styles.header}>Settings</Text>
      
      
      </TouchableOpacity>

      <View style={styles.profileCard}>
        <Ionicons name="person-circle-outline" size={70} color="#556B2F" style={{ marginRight: 16 }} />
        <View>
          <Text style={styles.name}>Lincy</Text>
          <Text style={styles.phone}>9876543210</Text>
          <Text style={styles.member}>daily Member</Text>
        </View>
      </View>

      <View style={styles.validityContainer}>
        <Text style={styles.validity}>
          Valid till <Text style={styles.bold}>03 Jun</Text>
        </Text>
      </View>

      <View style={styles.actionsRow}>
        <ActionCard title="Your Orders" icon="bag-outline" />
        <ActionCard title="Help & Support" icon="chatbubble-ellipses-outline" />
        <ActionCard title="Zepto Cash" icon="card-outline" />
      </View>

      <View style={styles.cardPurple}>
        <View style={styles.rowSpace}>
          <Text style={styles.sectionTitle}>Zepto Cash & Gift Card</Text>
          <Text style={styles.newTag}>NEW</Text>
        </View>
        <View style={styles.underline1} />
        <View style={styles.rowSpace}>
          <Text>Available Balance ₹0</Text>
          <TouchableOpacity style={styles.addBtn}>
            <Text style={styles.addBtnText}>Add Balance</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.rowAligned}>
        <View style={{ flex: 1, marginRight: 12 }}>
          <Text style={styles.bold}>Help us to know you better</Text>
        </View>
        <Image
          source={require('@/assets/images/writing pad.jpg')}
          style={styles.headerImage}
          resizeMode="cover"
        />
      </View> 

      <View style={styles.underline} />

      <View style={styles.preferenceBox}>
  <Text style={styles.question}>What are your food preferences?</Text>
  
  <View style={styles.optionsContainer}>
    {['Vegetarian', 'Non-vegetarian', 'Eggetarian'].map(option => (
      <TouchableOpacity
        key={option}
        style={[
          styles.option,
          preference === option && styles.optionSelected
        ]}
        onPress={() => setPreference(option)}
      >
        <View style={styles.radioCircle}>
          {preference === option && <View style={styles.radioDot} />}
        </View>
        <Text style={styles.optionLabel}>{option}</Text>
      </TouchableOpacity>
    ))}
  </View>
</View>
<View style={styles.section}>
  <Text style={styles.sectionHeading}>Your Information</Text>
  {[
    { label: 'Your Orders', icon: 'bag-outline' },
    { label: 'Help & Support', icon: 'chatbubble-ellipses-outline' },
    { label: 'Refunds', icon: 'cash-outline' },
    { label: 'Saved Addresses', icon: 'location-outline', subText: '2 Addresses' },
    { label: 'Profile', icon: 'person-outline' },
    { label: 'Payment Management', icon: 'card-outline' },
  ].map((item, index) => (
    <TouchableOpacity key={index} style={styles.infoRow}>
      <View style={styles.infoLeft}>
        <Ionicons name={item.icon} size={20} color="#000" style={{ marginRight: 12 }} />
        <View>
          <Text style={styles.infoLabel}>{item.label}</Text>
          {item.subText && <Text style={styles.subText}>{item.subText}</Text>}
        </View>
      </View>
      <Ionicons name="chevron-forward" size={20} color="#bbb" />
    </TouchableOpacity>
    
  ))}
</View>
<View style={styles.section}>
  <Text style={styles.sectionHeading}>Other Information</Text>
  {[
    { label: 'Suggest Products', icon: 'sparkles-outline' },
    { label: 'Notifications', icon: 'notifications-outline' },
    { label: 'General Info', icon: 'information-circle-outline' },
  ].map((item, index) => (
    <TouchableOpacity key={index} style={styles.infoRow}>
      <View style={styles.infoLeft}>
        <Ionicons name={item.icon} size={20} color="#000" style={{ marginRight: 12 }} />
        <Text style={styles.infoLabel}>{item.label}</Text>
      </View>
      <Ionicons name="chevron-forward" size={20} color="#bbb" />
    </TouchableOpacity>
  ))}
</View>

<TouchableOpacity style={styles.logoutButton}>
  <Text style={styles.logoutText}>Log Out</Text>
</TouchableOpacity>

<View style={styles.versionBlock}>
  <Text style={styles.versionText}>App version 25.5.4</Text>
  <Text style={styles.versionText}>v61-9</Text>
</View>

    </ScrollView>
  );
};

const ActionCard = ({ title, icon }) => (
  <TouchableOpacity style={styles.actionCard}>
    <Ionicons name={icon} size={20} color="black" />
    <Text style={styles.actionText}>{title}</Text>
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#e5e5e5' 
  },
  backIcon: { marginTop: 50,},
  header: { fontSize: 20, fontWeight: 'bold', marginLeft: 40, marginTop: -30, },
  header1:{
    marginBottom:20
  },
  profileCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fef9c3',
    padding: 16,
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
    marginTop:20
  },
  validityContainer: {
    backgroundColor: '#fff',
    paddingHorizontal: 8,
    paddingVertical: 10,
    borderBottomLeftRadius: 12,
    borderBottomRightRadius: 12,
    marginBottom: 30,
    minWidth: '100%',
    alignItems: 'flex-start'
  },
  validity: { fontSize: 14 },
  name: { fontSize: 18, fontWeight: 'bold' },
  phone: { color: '#555' },
  member: {
    fontSize: 12,
    color: 'white',
    backgroundColor: 'green',
    borderRadius: 10,
    paddingHorizontal: 8,
    paddingVertical: 2,
    marginTop: 4,
    alignSelf: 'flex-start'
  },
  bold: { fontWeight: 'bold' },
  actionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
    
  },
  actionCard: {
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 4,
    padding: 12,
    backgroundColor: '#f9fafb',
    borderRadius: 10
  },
  actionText: { marginTop: 4, fontSize: 12 },
  cardPurple: {
    backgroundColor: '#ede9fe',
    padding: 16,
    borderRadius: 12,
    marginBottom: 10
  },
  sectionTitle: { fontWeight: 'bold' },
  newTag: {
    backgroundColor: '#22c55e',
    color: 'white',
    paddingHorizontal: 6,
    borderRadius: 6,
    fontSize: 10,
  },
  rowSpace: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 6
  },
  addBtn: {
    backgroundColor: '#dbeafe',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6
  },
  addBtnText: { color: '#1d4ed8' },
  extraNote: {
    marginBottom: 16,
    fontSize: 13,
    color: '#4b5563'
  },
  question: { marginVertical: 30 },
  optionsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8
  },
  option: {
    padding: 10,
    borderRadius: 8,
    borderColor: '#e5e7eb',
    borderWidth: 1,
    marginRight: 8,
    marginBottom: 8
  },
  optionSelected: {
    backgroundColor: '#dbeafe',
    borderColor: '#2563eb'
  },
  headerImage: {
    width: 50,
    height: 50,
    borderRadius: 10,
    marginTop:15,
  },
  rowAligned: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: -10,
    marginBottom: 10
  },
  underline: {
    height: 1,
    backgroundColor: '#ccc',
    marginBottom: 30
  },
   underline1: {
    height: 1,
    backgroundColor: '#ccc',
    marginTop: 10,
  },
  preferenceBox: {
  borderWidth: 1,
  borderColor: '#ccc',
  borderRadius: 10,
  padding: 16,
  backgroundColor: '#fff',
  marginBottom: 30
},
question: {
  marginBottom: 16,
  fontWeight: 'bold',
  fontSize: 16
},
optionsContainer: {
  flexDirection: 'column',
  gap: 12
},
option: {
  flexDirection: 'row',
  alignItems: 'center',
  padding: 10,
  borderRadius: 8,
  borderWidth: 1,
  borderColor: '#ccc',
},
optionSelected: {
  backgroundColor: '#eef2ff',
  borderColor: '#2563eb'
},
radioCircle: {
  height: 18,
  width: 18,
  borderRadius: 9,
  borderWidth: 2,
  borderColor: '#2563eb',
  alignItems: 'center',
  justifyContent: 'center',
  marginRight: 12
},
radioDot: {
  height: 8,
  width: 8,
  borderRadius: 4,
  backgroundColor: '#2563eb'
},
optionLabel: {
  fontSize: 14,
  color: '#000'
},
section: {
  backgroundColor: '#fff',
  borderRadius: 12,
  paddingVertical: 8,
  marginBottom: 30
},
sectionHeading: {
  fontSize: 16,
  fontWeight: 'bold',
  paddingHorizontal: 16,
  marginBottom: 12,
  marginTop: 12
},
infoRow: {
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'space-between',
  paddingHorizontal: 16,
  paddingVertical: 14,
  borderBottomColor: '#eee',
  borderBottomWidth: 1
},
infoLeft: {
  flexDirection: 'row',
  alignItems: 'center',
},
infoLabel: {
  fontSize: 14,
  color: '#000'
},
subText: {
  fontSize: 12,
  color: '#777'
},
logoutButton: {
  backgroundColor: '#fff',
  paddingVertical: 14,
  marginHorizontal: 16,
  borderRadius: 10,
  alignItems: 'center',
  marginTop: 16,
  marginBottom: 10
},
logoutText: {
  color: '#000',
  fontWeight: 'bold'
},
versionBlock: {
  alignItems: 'center',
  marginBottom: 30
},
versionText: {
  fontSize: 12,
  color: '#666'
}
});

export default SettingsScreen;
