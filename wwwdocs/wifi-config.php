<?php
include('phpincs.php');
$output = $return = 0;
$page = $_GET['page'];


echo '<html>
<head>
<link href="styles.css" rel="stylesheet" type="text/css"></link>
<script type="text/Javascript" src="functions.js"></script>
<title>Raspbian WiFi Configuration Portal</title>
</head>
<body>
<div class="content">';
		exec('ifconfig wlan0',$return);
		exec('iwconfig wlan0',$return);
		$strWlan0 = implode(" ",$return);
		$strWlan0 = preg_replace('/\s\s+/', ' ', $strWlan0);
		preg_match('/HWaddr ([0-9a-f:]+)/i',$strWlan0,$result);
		$strHWAddress = $result[1];
		preg_match('/inet addr:([0-9.]+)/i',$strWlan0,$result);
		$strIPAddress = $result[1];
		preg_match('/Mask:([0-9.]+)/i',$strWlan0,$result);
		$strNetMask = $result[1];
		preg_match('/RX packets:(\d+)/',$strWlan0,$result);
		$strRxPackets = $result[1];
		preg_match('/TX packets:(\d+)/',$strWlan0,$result);
		$strTxPackets = $result[1];
		preg_match('/RX Bytes:(\d+ \(\d+.\d+ MiB\))/i',$strWlan0,$result);
		$strRxBytes = $result[1];
		preg_match('/TX Bytes:(\d+ \(\d+.\d+ [K|M|G]iB\))/i',$strWlan0,$result);
		$strTxBytes = $result[1];
		preg_match('/ESSID:\"([a-zA-Z0-9\s]+)\"/i',$strWlan0,$result);
		$strSSID = str_replace('"','',$result[1]);
		preg_match('/Access Point: ([0-9a-f:]+)/i',$strWlan0,$result);
		$strBSSID = $result[1];
		preg_match('/Bit Rate=([0-9]+ Mb\/s)/i',$strWlan0,$result);
		$strBitrate = $result[1];
		preg_match('/Tx-Power=([0-9]+ dBm)/i',$strWlan0,$result);
		$strTxPower = $result[1];
		preg_match('/Link Quality=([0-9]+\/[0-9]+)/i',$strWlan0,$result);
		$strLinkQuality = $result[1];
		preg_match('/Signal Level=(-[0-9]+ dBm)/i',$strWlan0,$result);
		$strSignalLevel = $result[1];
		if(strpos($strWlan0, "UP") !== false && strpos($strWlan0, "RUNNING") !== false) {
			$strStatus = '<span style="color:green">Interface is up</span>';
		} else {
			$strStatus = '<span style="color:red">Interface is down</span>';
		}
		if(isset($_POST['ifdown_wlan0'])) {
			exec('ifconfig wlan0 | grep -i running | wc -l',$test);
			if($test[0] == 1) {
				exec('sudo ifdown wlan0',$return);
			} else {
				echo 'Interface already down';
			}
			$_POST['ifdown_wlan0'] = null;
			unset($_POST['ifdown_wlan0']);
		} elseif(isset($_POST['ifup_wlan0'])) {
			exec('ifconfig wlan0 | grep -i running | wc -l',$test);
			if($test[0] == 0) {
				exec('sudo ifup wlan0',$return);
			} else {
				echo 'Interface already up';
			}
			$_POST['ifup_wlan0'] = null;
			unset($_POST['ifup_wlan0']);
		}
	echo '<div class="infobox">
<script>
function resetForm(id) {
	ifup_wlan0 = undefined;
	ifdown_wlan0 = undefined;
    document.getElementById(id).reset();
	document.location.reload(true);
}
</script>
<form action="" method="POST" id="ifconfig">
<input type="submit" value="ifdown wlan0" name="ifdown_wlan0" />
<input type="submit" value="ifup wlan0" name="ifup_wlan0" />
<input type="button" value="Refresh" onclick="resetForm(\'ifconfig\')" />
</form>
<div class="infoheader">Wireless Information and Statistics</div>
<div id="intinfo"><div class="intheader">Interface Information</div>
Interface Name : wlan0<br />
Interface Status : ' . $strStatus . '<br />
IP Address : ' . $strIPAddress . '<br />
Subnet Mask : ' . $strNetMask . '<br />
Mac Address : ' . $strHWAddress . '<br />
<div class="intheader">Interface Statistics</div>
Received Packets : ' . $strRxPackets . '<br />
Received Bytes : ' . $strRxBytes . '<br /><br />
Transferred Packets : ' . $strTxPackets . '<br />
Transferred Bytes : ' . $strTxBytes . '<br />
</div>
<div id="wifiinfo">
<div class="intheader">Wireless Information</div>
Connected To : ' . $strSSID . '<br />
AP Mac Address : ' . $strBSSID . '<br />
Bitrate : ' . $strBitrate . '<br />
Transmit Power : ' . $strTxPower .'<br />
Link Quality : ' . $strLinkQuality . '<br />
Signal Level : ' . $strSignalLevel . '<br />
</div>
</div>
<div class="intfooter">Information provided by ifconfig and iwconfig</div>';

		exec('sudo cat /etc/wpa_supplicant/wpa_supplicant.conf',$return_scan);
		$ssid = array();
		$psk = array();
		foreach($return_scan as $a) {
			if(preg_match('/SSID/i',$a)) {
				$arrssid = explode("=",$a);
				$ssid[] = str_replace('"','',$arrssid[1]);
			}
			if(preg_match('/\#psk/i',$a)) {
				$arrpsk = explode("=",$a);
				$psk[] = str_replace('"','',$arrpsk[1]);
			}
		}
		$numSSIDs = count($ssid);
		$output = '<form method="POST" action="" id="wpa_conf_form"><input type="hidden" id="Networks" name="Networks" /><div class="network" id="networkbox">';
		for($ssids = 0; $ssids < $numSSIDs; $ssids++) {
			$output .= '<div id="Networkbox'.$ssids.'" class="NetworkBoxes">Network '.$ssids.' <input type="button" value="Delete" onClick="DeleteNetwork('.$ssids.')" /></span><br />
<span class="tableft" id="lssid0">SSID :</span><input type="text" id="ssid0" name="ssid'.$ssids.'" value="'.$ssid[$ssids].'" onkeyup="CheckSSID(this)" /><br />
<span class="tableft" id="lpsk0">PSK :</span><input type="password" id="psk0" name="psk'.$ssids.'" value="'.$psk[$ssids].'" onkeyup="CheckPSK(this)" /></div>';
		}
		$output .= '</div><input type="submit" value="Scan for Networks" name="Scan" /><input type="button" value="Add Network" onClick="AddNetwork();" /><input type="submit" value="Save" name="SaveWPAPSKSettings" onmouseover="UpdateNetworks(this)" id="Save" />
</form>';

	echo $output;
	echo '<script type="text/Javascript">UpdateNetworks()</script>';

	if(isset($_POST['SaveWPAPSKSettings'])) {
		$config = 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

';
		$networks = $_POST['Networks'];
		for($x = 0; $x < $networks; $x++) {
			$network = '';
			$ssid = escapeshellarg($_POST['ssid'.$x]);
			$psk = escapeshellarg($_POST['psk'.$x]);
			exec('wpa_passphrase '.$ssid. ' ' . $psk,$network);
			foreach($network as $b) {
				$config .= "$b
";
			}
		}
		exec("echo '$config' > /tmp/wifidata",$return);
		system('sudo cp /tmp/wifidata /etc/wpa_supplicant/wpa_supplicant.conf',$returnval);
		if($returnval == 0) {
			echo "Wifi Settings Updated Successfully";
		} else {
			echo "Wifi settings failed to be updated";
		}
	} elseif(isset($_POST['Scan'])) {
		$return = '';
		exec('sudo wpa_cli scan',$return);
		sleep(5);
		exec('sudo wpa_cli scan_results',$return);
		for($shift = 0; $shift < 4; $shift++ ) {
			array_shift($return);
		}
		echo "Networks found : <br />";
		foreach($return as $network) {
			$arrNetwork = preg_split("/[\t]+/",$network);
			$bssid = $arrNetwork[0];
			$channel = ConvertToChannel($arrNetwork[1]);
			$signal = $arrNetwork[2] . " dBm";
			$security = $arrNetwork[3];
			$ssid = $arrNetwork[4];
			echo '<input type="button" value="Connect to This network" onClick="AddScanned(\''.$ssid.'\')" />' . $ssid . " on channel " . $channel . " with " . $signal . "(".ConvertToSecurity($security)." Security)<br />";

		}
	}

echo '
</div>
<div class="footer">
</div>
</body>
</html>';
?>