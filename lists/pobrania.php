<?php
header('Content-Type: text/plain');
$list = $_GET['list'] ?? '';
if($list && preg_match('/^[a-zA-Z0-9\s]+$/', $list)) {
    $file = 'pobrania.txt';
    $data = file_get_contents($file);
    $lines = explode("\n", $data);
    for($i=0; $i<count($lines); $i++) {
        if(strpos($lines[$i], $list) === 0) {
            list($name, $count) = explode(':', $lines[$i], 2);
            $lines[$i] = "$name: ".(intval(trim($count)) + 1);
            file_put_contents($file, implode("\n", $lines));
            break;
        }
    }
}
echo file_get_contents($file);
?>
