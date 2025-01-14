function string2Id(input) {
  // Si la chaîne commence par un chiffre, ajoute un underscore au début  
  // Remplacer les underscores par deux underscores  
  input = input.replace(/_/g, '__');

  if (/^\d/.test(input)) {
    input = '_' + input;
  }

  // Remplacer les caractères non alphanumériques (à l'exception de l'underscore)
  input = input.replace(/[^a-zA-Z0-9_]/g, (match) => {
      return '_' + match.charCodeAt(0).toString(16);
  });

  return input;
}

function stringOrInt(input) {
  const asInt = parseInt(input, 10);

  return isNaN(asInt) ? `"${input}"` : asInt;
}
