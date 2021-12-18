/* SuboptStructs.c : Implementation is somewhat tricky because the GTFold code is centered on 
 *                   printing the structures as they are found to an external file. This is not the 
 *                   behavior we necessarily want here;
 * Author: Maxie D. Schmidt (maxieds@gmail.com)
 * Created: 2020.02.07
 */

#include "SuboptStructs.h"
#include "Utils.h"

void FreeSSMapStructure(ss_ctype_t *ssMap, int mapLength) {
     if(ssMap == NULL || mapLength <= 0) {
          return;
     }
     for(int ssi = 0; ssi < mapLength; ssi++) {
          Free(ssMap[ssi].dotStruct);
     }
     Free(ssMap);
}

