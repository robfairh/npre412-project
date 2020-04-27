import os
import glob
import subprocess
import d3ploy.tester as tester
import d3ploy.plotter as plotter

demand_eq = '100'

control = """
<control>
    <duration>50</duration>
    <startmonth>1</startmonth>
    <startyear>2000</startyear>
    <decay>lazy</decay>
</control>
"""

archetypes = """
<archetypes>
    <spec>
        <lib>cycamore</lib>
        <name>Source</name>
    </spec>
    <spec>
        <lib>cycamore</lib>
        <name>Reactor</name>
    </spec>
    <spec>
        <lib>cycamore</lib>
        <name>Sink</name>
    </spec>
    <spec>
        <lib>agents</lib>
        <name>NullRegion</name>
    </spec>
    <spec>
        <lib>agents</lib>
        <name>NullInst</name>
    </spec>
    <spec>
        <lib>cycamore</lib>
        <name>DeployInst</name>
    </spec>
    <spec>
        <lib>d3ploy.demand_driven_deployment_inst</lib>
        <name>DemandDrivenDeploymentInst</name>
    </spec>
    <spec>
        <lib>d3ploy.supply_driven_deployment_inst</lib>
        <name>SupplyDrivenDeploymentInst</name>
    </spec>
</archetypes>
"""

source = """
<facility>
    <name>source</name>
    <config>
        <Source>
            <outcommod>sourceout</outcommod>
            <outrecipe>sourceoutrecipe</outrecipe>
            <throughput>1e6</throughput>
        </Source>
    </config>
</facility>
"""

lwr = """
<facility>
    <name>lwr</name>
    <lifetime>500</lifetime>
    <config>
    <Reactor>
        <fuel_inrecipes>
            <val>sourceoutrecipe</val>
        </fuel_inrecipes>
        <fuel_outrecipes>
            <val>lwroutrecipe</val>
        </fuel_outrecipes>
        <fuel_incommods>
            <val>sourceout</val>
        </fuel_incommods>
        <fuel_outcommods>
            <val>lwrout</val>
        </fuel_outcommods>
        <cycle_time>18</cycle_time>
        <refuel_time>0</refuel_time>
        <assem_size>20000</assem_size>
        <n_assem_core>3</n_assem_core>
        <n_assem_batch>1</n_assem_batch>
        <power_cap>1000</power_cap>
        <side_products> <val>hydrogen</val> </side_products>
        <side_product_quantity> <val>10</val> </side_product_quantity>
    </Reactor>
    </config>
</facility>
"""

hydrostorage = """
<facility>
    <name>hydrostorage</name>
    <config>
    <Sink>
        <in_commods>
            <val>hydrogen</val>
        </in_commods>
        <max_inv_size>1e10</max_inv_size>
    </Sink>
    </config>
</facility>
"""

reactorsink = """
<facility>
    <name>reactorsink</name>
    <config>
    <Sink>
        <in_commods>
            <val>lwrout</val>
        </in_commods>
        <max_inv_size>1e10</max_inv_size>
    </Sink>
    </config>
</facility>
"""

region = """
<region>
    <config>
    <NullRegion>
    </NullRegion>
    </config>

    <institution>
    <config>
    <DemandDrivenDeploymentInst>
        <calc_method>fft</calc_method>
        <demand_eq>100</demand_eq>
        <installed_cap>1</installed_cap>
        <back_steps>2</back_steps>
        <steps>1</steps>
        <driving_commod>hydrogen</driving_commod>
        <facility_commod>
        <item>
          <facility>source</facility>
          <commod>sourceout</commod>
        </item>
        <item>
          <facility>lwr</facility>
          <commod>hydrogen</commod>
        </item>
        </facility_commod>
        <facility_capacity>
        <item>
          <facility>source</facility>
          <capacity>1e6</capacity>
        </item>
        <item>
          <facility>lwr</facility>
          <capacity>10</capacity>
        </item>
        </facility_capacity>
    </DemandDrivenDeploymentInst>
    </config>
    <name>timeseriesinst</name>
    </institution>

    <institution>
    <config>
    <SupplyDrivenDeploymentInst>
        <calc_method>fft</calc_method>
        <back_steps>2</back_steps>
        <steps>1</steps>
        <facility_commod>
        <item>
            <facility>reactorsink</facility>
            <commod>lwrout</commod>
        </item>
        <item>
            <facility>hydrostorage</facility>
            <commod>hydrogen</commod>
        </item>
        </facility_commod>
        <facility_capacity>
        <item>
            <facility>reactorsink</facility>
            <capacity>1e10</capacity>
        </item>
        <item>
            <facility>hydrostorage</facility>
            <capacity>1e10</capacity>
        </item>
        </facility_capacity>
    </SupplyDrivenDeploymentInst>
    </config>
    <name>supplydrivendeploymentinst</name>
    </institution>

    <name>SingleRegion</name>
</region>
"""

recipe = """
<recipe>
    <name>sourceoutrecipe</name>
    <basis>mass</basis>
    <nuclide> <id>U234</id>  <comp>0.0002558883</comp> </nuclide>
    <nuclide> <id>U235</id>  <comp>0.0319885317</comp> </nuclide>
    <nuclide> <id>U238</id>  <comp>0.96775558</comp> </nuclide>
</recipe>

<recipe>
    <name>lwroutrecipe</name>
    <basis>mass</basis>
    <nuclide> <id>He4</id>  <comp>9.47457840128509E-07</comp> </nuclide>
    <nuclide> <id>Ra226</id>  <comp>9.78856442957042E-14</comp> </nuclide>
    <nuclide> <id>Ra228</id>  <comp>2.75087759176098E-20</comp> </nuclide>
    <nuclide> <id>Pb206</id>  <comp>5.57475193532078E-18</comp> </nuclide>
    <nuclide> <id>Pb207</id>  <comp>1.68592497990149E-15</comp> </nuclide>
    <nuclide> <id>Pb208</id>  <comp>3.6888358546006E-12</comp> </nuclide>
    <nuclide> <id>Pb210</id>  <comp>3.02386544437848E-19</comp> </nuclide>
    <nuclide> <id>Th228</id>  <comp>8.47562285269577E-12</comp> </nuclide>
    <nuclide> <id>Th229</id>  <comp>2.72787861516683E-12</comp> </nuclide>
    <nuclide> <id>Th230</id>  <comp>2.6258831537493E-09</comp> </nuclide>
    <nuclide> <id>Th232</id>  <comp>4.17481422959E-10</comp> </nuclide>
    <nuclide> <id>Bi209</id>  <comp>6.60770597104927E-16</comp> </nuclide>
    <nuclide> <id>Ac227</id>  <comp>3.0968621961773E-14</comp> </nuclide>
    <nuclide> <id>Pa231</id>  <comp>9.24658854635179E-10</comp> </nuclide>
    <nuclide> <id>U232</id>  <comp>0.000000001</comp> </nuclide>
    <nuclide> <id>U233</id>  <comp>2.21390148606282E-09</comp> </nuclide>
    <nuclide> <id>U234</id>  <comp>0.0001718924</comp> </nuclide>
    <nuclide> <id>U235</id>  <comp>0.0076486597</comp> </nuclide>
    <nuclide> <id>U236</id>  <comp>0.0057057461</comp> </nuclide>
    <nuclide> <id>U238</id>  <comp>0.9208590237</comp> </nuclide>
    <nuclide> <id>Np237</id>  <comp>0.0006091729</comp> </nuclide>
    <nuclide> <id>Pu238</id>  <comp>0.000291487</comp> </nuclide>
    <nuclide> <id>Pu239</id>  <comp>0.0060657301</comp> </nuclide>
    <nuclide> <id>Pu240</id>  <comp>0.0029058707</comp> </nuclide>
    <nuclide> <id>Pu241</id>  <comp>0.0017579218</comp> </nuclide>
    <nuclide> <id>Pu242</id>  <comp>0.0008638616</comp> </nuclide>
    <nuclide> <id>Pu244</id>  <comp>2.86487251922763E-08</comp> </nuclide>
    <nuclide> <id>Am241</id>  <comp>6.44271331287386E-05</comp> </nuclide>
    <nuclide> <id>Am242m</id>  <comp>8.53362027193319E-07</comp> </nuclide>
    <nuclide> <id>Am243</id>  <comp>0.0001983912</comp> </nuclide>
    <nuclide> <id>Cm242</id>  <comp>2.58988475560194E-05</comp> </nuclide>
    <nuclide> <id>Cm243</id>  <comp>0.000000771</comp> </nuclide>
    <nuclide> <id>Cm244</id>  <comp>8.5616190260478E-05</comp> </nuclide>
    <nuclide> <id>Cm245</id>  <comp>5.72174539442251E-06</comp> </nuclide>
    <nuclide> <id>Cm246</id>  <comp>7.29567535786554E-07</comp> </nuclide>
    <nuclide> <id>Cm247</id>  <comp>0.00000001</comp> </nuclide>
    <nuclide> <id>Cm248</id>  <comp>7.69165773748653E-10</comp> </nuclide>
    <nuclide> <id>Cm250</id>  <comp>4.2808095130239E-18</comp> </nuclide>
    <nuclide> <id>Cf249</id>  <comp>1.64992658175413E-12</comp> </nuclide>
    <nuclide> <id>Cf250</id>  <comp>2.04190913935875E-12</comp> </nuclide>
    <nuclide> <id>Cf251</id>  <comp>9.86556100338561E-13</comp> </nuclide>
    <nuclide> <id>Cf252</id>  <comp>6.57970721693466E-13</comp> </nuclide>
    <nuclide> <id>H3</id>  <comp>8.58461800264195E-08</comp> </nuclide>
    <nuclide> <id>C14</id>  <comp>4.05781943561107E-11</comp> </nuclide>
    <nuclide> <id>Kr81</id>  <comp>4.21681236076192E-11</comp> </nuclide>
    <nuclide> <id>Kr85</id>  <comp>3.44484671160181E-05</comp> </nuclide>
    <nuclide> <id>Sr90</id>  <comp>0.0007880649</comp> </nuclide>
    <nuclide> <id>Tc99</id>  <comp>0.0011409492</comp> </nuclide>
    <nuclide> <id>I129</id>  <comp>0.0002731878</comp> </nuclide>
    <nuclide> <id>Cs134</id>  <comp>0.0002300898</comp> </nuclide>
    <nuclide> <id>Cs135</id>  <comp>0.0006596706</comp> </nuclide>
    <nuclide> <id>Cs137</id>  <comp>0.0018169192</comp> </nuclide>
    <nuclide> <id>H1</id>  <comp>0.0477938151</comp> </nuclide>
</recipe>
"""

direc = os.listdir('./')
ENV = dict(os.environ)
ENV['PYTHONPATH'] = ".:" + ENV.get('PYTHONPATH', '')
hit_list = glob.glob('*.sqlite')
for file in hit_list:
	os.remove(file)

input_file = 'transition1.xml'
output_file = 'transition1.sqlite'

with open(input_file, 'w') as f:
    f.write('<simulation>\n')
    f.write(control + archetypes)
    f.write(source)
    f.write(lwr)
    f.write(hydrostorage)
    f.write(reactorsink)
    f.write(region)
    f.write(recipe)
    f.write('</simulation>\n')

s = subprocess.check_output(['cyclus', '-o', output_file, input_file], universal_newlines=True, env=ENV)

# Initialize dicts
all_dict = {}
agent_entry_dict = {}

# get agent deployment
commod_dict = {'sourceout': ['source'],
               'hydrogen': ['lwr'],
               'lwrout': ['reactorsink']}

for commod, facility in commod_dict.items():
    agent_entry_dict[commod] = tester.get_agent_dict(output_file, facility)

# get supply demand dict
all_dict['hydrogen'] = tester.supply_demand_dict_driving(
    output_file, demand_eq, 'hydrogen')

plotter.plot_demand_supply_agent(all_dict['hydrogen'],
                                 agent_entry_dict['hydrogen'], 'hydrogen',
                                 'flatpower-d3ploy_hydrogen',
                                 True, True, False, 1)
