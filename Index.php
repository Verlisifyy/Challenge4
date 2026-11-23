<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
$naam = $_POST["naam"];
$geboortejaar = $_POST["geboortejaar"];

   $leeftijd = date("Y") - $geboortejaar;

echo "Hallo " . $naam;
echo "<br>";
echo "Je bent " . $leeftijd . " jaar oud.";
}
?>

<!DOCTYPE html>
<html>
<head>
  <title>Leeftijd berekenen</title>
</head>

<body> 
    <form action="index.php" method="POST">
     <p>Wat is je naam?</p>
           <input type="text" name="naam">
     <p>wat is je geboortejaar?</p>
          <input type="number" name="geboortejaar">
                <button type="submit">Versturen</button>
    </form>
</body>

</html>

<!--php vertelt dat PHP begint if controleert 
if het verstuurd is $_server["request_method"] controleert welke methode gebruikt is
date y neemt het jaar wat nu is en - geboorejaar neemt die jaren daar van af
Echo Laat de resulataten laten zien br laat een nieuwe regel zien  $laat een veriabele zien
in body staat de inhoud van de pagina form en maakt invoervelden aan een button om te versturen-->