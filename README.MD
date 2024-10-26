# Requirements

Is het buiten warmer dan binnen moet het verwarmingselement inschakelen tot de warmte binnen hoger is dan buiten. 


Het vochtgehalte moet dan afgestemd worden op de heersende temperatuur en deze info zou uit een tabel gehaald moeten worden. 
Het programma moet dus de temperatuur en het vochtgehalte gaan vergelijken met een tabel en indien het vochtgehalte lager is, 
moet dit een puls geven naar de stoominstallatie om het vochtgehalte te verhogen.




als temp_buiten > temp_binnen:
    verwarm 

als vocht gehalte < vocht gehalte tabel
    stoom


