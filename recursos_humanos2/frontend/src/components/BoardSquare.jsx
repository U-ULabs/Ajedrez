import React from 'react';
import { getPieceImage } from '../utils';

const BoardSquare = ({ x, y, piece, isFog, isSelected, onClick, isLastMove }) => {
    const isDark = (x + y) % 2 === 1;
    const bgColor = isDark ? '#b58863' : '#f0d9b5';

    // Style for fog
    const fogStyle = {
        backgroundColor: '#14141e',
        opacity: 0.95,
        cursor: 'default'
    };

    // Style for square
    const squareStyle = {
        width: '60px',
        height: '60px',
        backgroundColor: isSelected ? 'rgba(255, 255, 0, 0.5)' : bgColor,
        position: 'relative',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        cursor: 'pointer',
        border: isSelected ? '2px solid yellow' : (isLastMove ? '2px solid red' : 'none')
    };

    if (isFog) {
        return (
            <div style={{ ...squareStyle, ...fogStyle }}>
                {/* Fog hides everything */}
            </div>
        );
    }

    return (
        <div style={squareStyle} onClick={() => onClick(x, y)}>
            {piece && (
                <div style={{ position: 'relative', width: '100%', height: '100%' }}>
                    <img
                        src={getPieceImage(piece.tipo, piece.team, piece.es_boss)}
                        alt={piece.tipo}
                        style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                    />
                    {/* HP Bar */}
                    <div style={{
                        position: 'absolute',
                        top: '2px',
                        left: '2px',
                        right: '2px',
                        height: '4px',
                        backgroundColor: 'black',
                        border: '1px solid white'
                    }}>
                        <div style={{
                            width: `${(piece.hp / piece.hp_max) * 100}%`,
                            height: '100%',
                            backgroundColor: (piece.hp / piece.hp_max) > 0.5 ? 'green' : 'red'
                        }} />
                    </div>
                </div>
            )}

            {/* Coordinate label for debug (optional) */}
            {/* <span style={{ position: 'absolute', bottom: 0, right: 0, fontSize: '8px' }}>{x},{y}</span> */}
        </div>
    );
};

export default BoardSquare;
