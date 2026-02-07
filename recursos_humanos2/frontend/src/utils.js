export const getPieceImage = (type, team, isBoss) => {
    if (isBoss) return '/images/boss.png';

    const color = team === 'JUGADOR' ? 'blanco' : 'negro';
    const colorA = team === 'JUGADOR' ? 'blanca' : 'negra';

    switch (type) {
        case 'PEON': return `/images/peon_${color}.png`;
        case 'CABALLO': return `/images/caballo_${color}.png`;
        case 'ALFIL': return `/images/alfil_${color}.png`;
        case 'TORRE': return `/images/torre_${colorA}.png`;
        case 'REINA': return `/images/reina_${colorA}.png`;
        case 'REY': return `/images/rey_${color}.png`;
        default: return null;
    }
};
