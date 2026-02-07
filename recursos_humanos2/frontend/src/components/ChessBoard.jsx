import React, { useState, useEffect } from 'react';
import BoardSquare from './BoardSquare';
import { getGameState, movePiece, resetGame } from '../services/api';

const ChessBoard = () => {
    const [gameState, setGameState] = useState(null);
    const [selectedPiece, setSelectedPiece] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchState();
        // Poll every 2 seconds to update AI moves if we want simple polling
        const interval = setInterval(fetchState, 2000);
        return () => clearInterval(interval);
    }, []);

    const fetchState = async () => {
        const state = await getGameState();
        if (state) {
            setGameState(state);
            setLoading(false);
        } else {
            setError("Failed to load game state");
            setLoading(false);
        }
    };

    const handleSquareClick = async (x, y) => {
        if (!gameState || gameState.game_over) return;

        // If fog, can't select (unless we want to allow blind clicking? No, fog means unknown)
        // Actually, backend might say it's fog, but if we have a piece there we should know?
        // Logic: if fog is true, we display fog.
        // If we click fog, we probably shouldn't be able to select anything unless it's our piece that is just hidden? 
        // But our pieces clear fog. So fog squares are empty or enemy.

        // Find piece at x, y
        const piece = gameState.piezas.find(p => p.x === x && p.y === y);
        const isFog = gameState.niebla[y][x];

        if (selectedPiece) {
            // Try to move
            if (selectedPiece.x === x && selectedPiece.y === y) {
                // Deselect
                setSelectedPiece(null);
            } else {
                // Attempt move
                const result = await movePiece(selectedPiece.x, selectedPiece.y, x, y);
                if (result.success) {
                    setGameState(result.state);
                    setSelectedPiece(null);
                } else {
                    // Invalid move or other error
                    // If clicked another own piece, select that instead
                    if (piece && piece.team === 'JUGADOR') {
                        setSelectedPiece(piece);
                    } else {
                        // alert(result.message); // Optional feedback
                        setSelectedPiece(null);
                    }
                }
            }
        } else {
            // Select piece
            if (piece && piece.team === 'JUGADOR') {
                setSelectedPiece(piece);
            }
        }
    };

    const handleReset = async () => {
        const result = await resetGame();
        if (result && result.success) {
            setGameState(result.state);
            setSelectedPiece(null);
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    if (!gameState) return <div>No game state</div>;

    // Render 8x8 grid
    const board = [];
    for (let y = 0; y < 8; y++) {
        const row = [];
        for (let x = 0; x < 8; x++) {
            const piece = gameState.piezas.find(p => p.x === x && p.y === y);
            const isFog = gameState.niebla[y][x];
            const isSelected = selectedPiece && selectedPiece.x === x && selectedPiece.y === y;

            row.push(
                <BoardSquare
                    key={`${x}-${y}`}
                    x={x}
                    y={y}
                    piece={piece}
                    isFog={isFog}
                    isSelected={isSelected}
                    onClick={handleSquareClick}
                />
            );
        }
        board.push(<div key={y} style={{ display: 'flex' }}>{row}</div>);
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div style={{ marginBottom: '10px', fontSize: '1.2em' }}>
                Turno: {gameState.turno === 'JUGADOR' ? 'Tu Turno' : 'IA Pensando...'}
            </div>

            {gameState.game_over && (
                <div style={{
                    color: gameState.winner === 'PLAYER' ? 'green' : 'red',
                    fontSize: '2em',
                    fontWeight: 'bold',
                    margin: '10px'
                }}>
                    {gameState.winner === 'PLAYER' ? '¡VICTORIA!' : '¡DERROTA!'}
                </div>
            )}

            <div style={{ border: '5px solid #5c4033' }}>
                {board}
            </div>

            <button
                onClick={handleReset}
                style={{ marginTop: '20px', padding: '10px 20px', fontSize: '1em', cursor: 'pointer' }}
            >
                Reiniciar Partida
            </button>

            {/* Logs Area */}
            <div style={{
                marginTop: '20px',
                backgroundColor: '#eee',
                padding: '10px',
                width: '480px',
                maxHeight: '100px',
                overflowY: 'auto',
                border: '1px solid #ccc',
                textAlign: 'left'
            }}>
                {gameState.logs && gameState.logs.map((log, i) => (
                    <div key={i}>{log}</div>
                ))}
            </div>
        </div>
    );
};

export default ChessBoard;
